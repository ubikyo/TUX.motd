import psutil
import ipaddress
import subprocess
import re
import platform
import os

from tux_motd.misc.module import Module
from tux_motd.misc.i18n import _, _n, col
from tux_motd.misc.util import has_command, is_root
from tux_motd.misc.ui import Display
from tux_motd.misc.configuration import Configuration
from tux_motd.misc.theme import theme

class Network(Module):

    settings = {}

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        self.interface()
        self.route()
        self.resolver()
        self.firewall()

    def interface(self):
        """ Affiche les interfaces réseaux """

        if self.get("show", True):

            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()

            ifaces = set()         

            for iface, addrs in interfaces.items():
                if stats.get(iface) and stats[iface].isup:
                    status = _("Up")
                    status_color = theme.Ok
                else:
                    status = _("Down")
                    status_color = theme.Critical

                for addr in addrs:
                    if addr.family == 10 and iface not in self.get("exclude", []):
                        if self.get("ipv6", False):
                            net = ipaddress.IPv6Network(f"{addr.address}")
                            ip  = f"{addr.address}/{net.prefixlen}"

                            ifaces.add((
                                iface,
                                status,
                                ip
                            ))
                        else:
                            continue

                    if addr.family == 2 and iface not in self.get("exclude", []):
                        if self.get("ipv4", True):
                            if addr.netmask:
                                net = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                                ip  = f"{addr.address}/{net.prefixlen}"
                            else:
                                ip  = addr.address

                            ifaces.add((
                                iface,
                                status,
                                ip
                            ))
                        else:
                            continue

            if ifaces:

                Display.header(
                    f"{_n('Interface', 'Interfaces', len(ifaces)):22}"
                    f"{_('Address'):44}"
                    f"{_('Status')}"
                )

                for iface, status, ip in ifaces:
                    print(
                        f"   {theme.Bright}{theme.Highlight}"
                        f"{self.get('icon','󱦂')}  "
                        f"{iface:16}{theme.Reset}"
                        f"{ip:44}"
                        f"{status_color}{status}\r"
                    )

    def route(self):
        """ Affiche les routes """

        if self.get("show", True):

            ipv4_routes = []
            if self.get("ipv4", True):
                ipv4_routes = self.get_routes(ipv6=False)

            ipv6_routes = []
            if self.get("ipv6", False):
                ipv6_routes = self.get_routes(ipv6=True)

            def tri(routes):
                return sorted(routes, key=lambda r: (not r["default"], r["destination"]))

            all_routes = tri(ipv4_routes) + tri(ipv6_routes)

            Display.header(
                f"{_n('Route' , 'Routes', len(all_routes)):22}" +
                f"{_('Gateway'):44}" +
                col("Metric", len(f"Metric")) +
                f"{_('Destination')}"
            )

            if all_routes:

                for route in all_routes:
                    metric = route["metric"] if route["metric"] else "0"
                    default = "Default" if route["destination"] == "default" else route["destination"] 
                    status_color = theme.Ok if default == "Default" else theme.Reset

                    print(
                        f"   {theme.Bright}{theme.Highlight}" +
                        f"{self.get('icon','󱇢')}  " +
                        f"{route['interface']:16}{theme.Reset}" +
                        f"{route['gateway']:44}" +
                        col(metric, None, "Metric") +
                        f"{status_color}{default}{theme.Reset}\r"
                    )

    def get_routes(self, ipv6=False):
        """ 
            Obtient les routes du système
            Args:
                ipv6 (bool): True pour IPv6, False pour IPv4.
            Returns:
                list: Une liste de dictionnaires contenant les routes.
        """
        cmd = ["ip", "-6", "route"] if ipv6 else ["ip", "-4", "route"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        routes = []

        for line in result.stdout.strip().splitlines():
            route = {
                "family": "IPv6" if ipv6 else "IPv4",
                "default": line.startswith("default"),
                "destination": "",
                "gateway": "",
                "interface": "",
                "src": "",
                "metric": ""
            }

            parts = line.split()
            i = 0
            while i < len(parts):
                if parts[i] == "default":
                    route["destination"] = "default"
                elif i == 0 and not line.startswith("default"):
                    route["destination"] = parts[i]
                elif parts[i] == "via":
                    route["gateway"] = parts[i + 1]
                    i += 1
                elif parts[i] == "dev":
                    route["interface"] = parts[i + 1]
                    i += 1
                elif parts[i] == "src":
                    route["src"] = parts[i + 1]
                    i += 1
                elif parts[i] == "metric":
                    route["metric"] = parts[i + 1]
                    i += 1
                i += 1

            if (route["interface"] not in self.get("exclude", [])):
                routes.append(route)

            return routes

    def resolver(self):
        """ Affiche les resolvers """

        if self.get("show", True):

            result = subprocess.run(
                ["resolvectl", "status"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True
            )

            interfaces = {}
            interface = None
            fallback_dns = []

            for line in result.stdout.splitlines():
                line = line.strip()

                if match := re.match(r"^Link\s+\d+\s+\(([\w\.\-]+)\)", line):
                    interface = match.group(1)

                    interfaces[interface] = {
                        "dns_servers": [],
                        "dns_domain": None,
                        "default_route": False,
                        "current_scopes": ""
                    }
                elif interface:
                    if line.startswith("DNS Servers:"):
                        servers = line.split(":", 1)[1].strip().split()
                        interfaces[interface]["dns_servers"].extend(servers)
                    elif line.startswith("DNS Domain:"):
                        domain = line.split(":", 1)[1].strip()
                        interfaces[interface]["dns_domain"] = domain
                    elif line.startswith("Default Route:"):
                        is_default = line.split(":", 1)[1].strip().lower() == "yes"
                        interfaces[interface]["default_route"] = is_default
                    elif line.startswith("Current Scopes:"):
                        scopes = line.split(":", 1)[1].strip()
                        interfaces[interface]["current_scopes"] = scopes

                elif line.startswith("Fallback DNS Servers:"):
                    servers = line.split(":", 1)[1].strip().split()
                    fallback_dns.extend(servers)

            if fallback_dns:
                interfaces["fallback"] = {
                    "dns_servers": fallback_dns,
                    "dns_domain": None,
                    "default_route": True,
                    "current_scopes": "DNS"
                }

            filtered = {
                name: data for name, data in interfaces.items()
                if data["current_scopes"].strip() == "DNS" and name not in self.get("exclude", [])
            }

            if not filtered:
                Display.label(
                    self.get("icon","󰖟"),
                    _("Resolvers"),
                    _("None"), 3
                )
            else:
                Display.header(
                    f"{_n('Resolver' , 'Resolvers', len(filtered)):22}" +
                    col("Default", len(_("Default"))) +
                    col("Domain search", 35) +
                    col("IP address")
                )

                for interface in filtered:
                    info = filtered[interface]
                    dns_servers = []

                    for dns_server in info["dns_servers"]:
                        ip_address = ipaddress.ip_address(dns_server)
                        if (isinstance(ip_address, ipaddress.IPv4Address) and self.get("ipv4", True)) or \
                        (isinstance(ip_address, ipaddress.IPv6Address) and self.get("ipv6", False)):
                            dns_servers.append(dns_server)

                    default = _("Yes") if info["default_route"] else _("No")
                    default_color = theme.Ok if info["default_route"] else theme.Reset
                    domain_search = info["dns_domain"] if info["dns_domain"] else _("None")

                    print(
                        f"   {theme.Bright}{theme.Highlight}{self.get('icon','󰖟')}  " +
                        col(interface, 16) +
                        f"{theme.Reset}{default_color}" +
                        col(default, None, "Default") +
                        f"{theme.Reset}" +
                        col(domain_search, 35, "Domain search") +
                        f"{', '.join(dns_servers)}{theme.Reset}\r"
                    )

    def detect_ip_version(self, ip):
        ip_obj = ipaddress.ip_address(ip)
        if isinstance(ip_obj, ipaddress.IPv4Address):
            return "IPv4"
        elif isinstance(ip_obj, ipaddress.IPv6Address):
            return "IPv6"
    
    def firewall(self):
        """ Affiche les règles du parefeu """

        system = platform.system()

        if (has_command("ufw") and is_root() and self.get("show", True)):

            env = os.environ.copy()

            env["LANG"] = "en_US.UTF-8"
            env["LC_ALL"] = "en_US.UTF-8"

            result = subprocess.run(["ufw", "status","verbose"], stdout=subprocess.PIPE, universal_newlines=True, env=env)

            icon =   self.get("icon", "󰕥")
            status = _("Status")

            if ("inactive" in result.stdout):
                Display.header(_("Firewall"))
                Display.label(
                    icon, 
                    status, 
                    f"{theme.Critical}{_('Inactive')}{theme.Reset}", 
                    3
                )

            elif ("active" in result.stdout and len(result.stdout.splitlines()) == 1):
                Display.header("Firewall")
                Display.label(
                    icon, 
                    status, 
                    f"{theme.Warning}{_('No rules')}{theme.Reset}", 
                    3
                )

            elif ("---" in result.stdout):
                Display.header(
                    f"{_('Firewall'):44}"
                    f"{_('Type'):7}"
                    f"{_('Action'):8}"
                    f"{_('Dir'):5}"
                    f"{_('Rule')}"
                )

                after_separator = False
                for line in result.stdout.splitlines():
                    if not after_separator:
                        if line.strip().startswith("--"):
                            after_separator = True
                        continue
                    if "v6" in line and not self.get("ipv6", False):
                        continue
                    if not line.strip():
                        continue
                    if not "v6" in line and not self.get("ipv4", True):
                        continue
                    
                    regex = r"^(.+?)\s+(ALLOW|DENY|REJECT|LIMIT)(?:\s+(IN))?\s+(.+?)(?:\s+\(v6\))?$"
                    
                    match = re.match(regex, line)

                    direction = ("IN" if "IN" in match.group(3) else "OUT")
                    description = match.group(1).replace(" (v6)", "") 
                    type = "IPv6" if "v6" in line else "IPv4"

                    if match:
                        print(
                            f"   {theme.Bright}{theme.Highlight}{icon}  "
                            f"{description:38}{theme.Reset}"
                            f"{type:7}"
                            f"{match.group(2):8}"
                            f"{direction:5}"
                            f"{match.group(4)}\r"
                        )