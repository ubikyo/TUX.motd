import psutil

from tux_motd.misc.module import Module
from tux_motd.misc.i18n import _, _n
from tux_motd.misc.ui import Display
from tux_motd.misc.configuration import Configuration
from tux_motd.misc.theme import theme

class Memory(Module):

    settings = {}

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        """ Affiche l"état de la mémoire """

        Display.header(_("Memory"))

        mem = psutil.virtual_memory()

        Display.barlabel(
            self.get("icon.info",""), 
            "", 
            mem.used, 
            mem.total,
            Configuration.get("graph.width", 50)
        )
        
        Display.bargraph(
            self.get("icon.graph",""), 
            mem.used, 
            mem.total,
            self.get("treshold.warn", 70),
            self.get("treshold.critical", 90),
            Configuration.get("graph.width", 50)
        )
