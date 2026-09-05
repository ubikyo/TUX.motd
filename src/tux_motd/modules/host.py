import pyfiglet
import socket
import distro
import psutil
import subprocess
import os

from datetime import datetime

from tux_motd.misc.module import Module
from tux_motd.misc.i18n import _, _n
from tux_motd.misc.ui import Display
from tux_motd.misc.configuration import Configuration
from tux_motd.misc.theme import theme, Foreground

class Host(Module):

    settings = {}

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        """ Affiche l"état de l'hôee """
        self.hostname()
        self.distro()
        self.uptime()
        self.update()
        self.banner()

    def hostname(self):
        """ Affiche le nom de l'hôte via figlet """

        print(f"{Foreground.get(Configuration.get('theme.hostname'), theme.Hostname)}%s{theme.Reset}" % 
            pyfiglet.figlet_format(
                self.get_name(), 
                font=self.get('font', 'termius'), 
                width=1000)
            )
            
    def get_name(self):
        """ Obtient le nom court du système """

        return socket.gethostname().split(".")[0]

    def distro(self):
        """ Affiche la distribution et sa version """

        Display.label(
            self.get("icon", ""), 
            distro.name(), 
            distro.version()
        )

    def uptime(self):
        """ Affiche l"uptime depuis le dernier boot """

        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time

        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)

        Display.label(
            self.get("icon", ""), 
            _("Uptime"),
            ( 
                f"{days} {  _n('day', 'days', days)}", 
                f"{hours} { _n('hour', 'hours', hours)}"
            )
        )

    def update(self):
        """ Affiche les mises à jours disponibles """

        env = os.environ.copy()

        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"

        result = subprocess.run(
            ["apt", "list", "--upgradable"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env
        )

        upgradable = [line for line in result.stdout.splitlines() if "/" in line and not line.startswith("Listing")]

        Display.header(
            f"{_n('Update', 'Updates', len(upgradable)):22}"
            f"{_('Count')}"
        )

        Display.label(
            self.get("icon","󰏓"), 
            _n("Package", "Packages", len(upgradable)), 
            len(upgradable), 
            3
        )

    def banner(self):
        messages = self.get("message", None)

        if messages:
            for user, message in messages.items():
                if user == 'all' or user == os.getlogin():
                    Display.box(
                        message, 
                        Configuration.get("box.width", 50),
                        Foreground.get(Configuration.get("box.color"), theme.Highlight)
                    )