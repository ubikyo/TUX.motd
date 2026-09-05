import psutil

from tux_motd.misc.module import Module
from tux_motd.misc.i18n import _, _n
from tux_motd.misc.ui import Display
from tux_motd.misc.theme import theme

class Processor(Module):

    settings = {}

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        self.processorsinfo()
        self.loadaverage()

    def processorsinfo(self):
        """ Affiche les informations sur le/les CPU """

        cpu_count  = psutil.cpu_count(logical=True)
        core_count = psutil.cpu_count(logical=True) * psutil.cpu_count(logical=False)

        Display.header(_n("Processor","Processors", cpu_count))

        print(
            f"   {self.get('icon.info', '')}  "
            f"{cpu_count} {  _n('Socket', 'Sockets', cpu_count)} / "
            f"{core_count} { _n('Total core', 'Total cores', core_count)}\r"
        )

    def loadaverage(self):
        """ Affiche la charge CPU """

        load1, load5, load15 = psutil.getloadavg()

        cpu_count = psutil.cpu_count(logical=True)

        load1  = self.get_loadaverage_color(1,  load1,  cpu_count)
        load5  = self.get_loadaverage_color(5,  load5,  cpu_count)
        load15 = self.get_loadaverage_color(15, load15, cpu_count)

        print(
            f"   {self.get('icon.graph','')}  "
            f"{load1}  {load5}  {load15}\r"
        )

    def get_loadaverage_color(self, during, value, cpu_count):
        """ Donne une couleur à la charge CPU en fonction d"un seuil """
        
        if value <= cpu_count:
            color = theme.Ok
        elif value <=(cpu_count * 2):
            color = theme.Warning
        else:
            color = theme.Critical

        return f"{theme.Bright}{theme.Highlight}{during}{_('m')}{theme.Reset} {color}{value:.2f}" 
