import psutil

from tux_motd.misc.module import Module
from tux_motd.misc.i18n import _, _n
from tux_motd.misc.ui import Display
from tux_motd.misc.configuration import Configuration
from tux_motd.misc.theme import theme

class Disk(Module):

    settings = {}

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        """ Affiche les disques attachés au système """
            
        parts = psutil.disk_partitions(all=False)

        if (parts):

            volumes = set()

            for part in parts:
                try:
                    if any(part.mountpoint.startswith(prefix) for prefix in self.get("exclude", [])):
                        continue
                    usage = psutil.disk_usage(part.mountpoint)
                    volumes.add((
                        part.mountpoint,
                        usage.used,
                        usage.total
                    ))
                except PermissionError:
                    continue

            if (volumes):
                Display.header(_n("Disk", "Disks", len(volumes)))

                for i, (mountpoint, used, total) in enumerate(volumes, start=1):

                    if i != 1:
                        print("")

                    Display.barlabel(
                        self.get("icon.info",""), 
                        mountpoint, 
                        used, 
                        total, 
                        Configuration.get("graph.width", 50)
                    )

                    Display.bargraph(
                        self.get("icon.graph",""), 
                        used, 
                        total, 
                        self.get("treshold.warn", 70),
                        self.get("treshold.critical", 90),
                        Configuration.get("graph.width", 50)
                    )