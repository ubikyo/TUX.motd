
from colorama import Fore, Style, init

from tux_motd.misc.configuration import Configuration

Foreground = {
    "black":    Fore.BLACK,
    "red":      Fore.RED,
    "green":    Fore.GREEN,
    "yellow":   Fore.YELLOW,
    "blue":     Fore.BLUE,
    "magenta":  Fore.MAGENTA,
    "cyan":     Fore.CYAN,
    "white":    Fore.WHITE,
    "reset":    Fore.RESET
}

class Theme:

    init(autoreset=True, strip=False, convert=False)

    def __init__(self):
        pass

    @property
    def Ok(cls):
        return Foreground.get(Configuration.get("theme.ok"), Fore.GREEN)
    
    @property
    def Warning(cls):
        return Foreground.get(Configuration.get("theme.warning"), Fore.MAGENTA)

    @property
    def Critical(cls):
        return Foreground.get(Configuration.get("theme.critical"), Fore.RED)

    @property
    def Highlight(cls):
        return Foreground.get(Configuration.get("theme.highlight"), Fore.YELLOW)

    @property
    def Hostname(cls):
        return Foreground.get(Configuration.get("theme.hostname"), Fore.GREEN)

    @property
    def Title(cls):
        return Foreground.get(Configuration.get("theme.title"), Fore.WHITE)

    @property
    def Reset(cls):
        return Style.RESET_ALL
    
    @property
    def Bright(cls):
        return Style.BRIGHT

    @property
    def Dim(cls):
        return Style.DIM
    
    @property
    def LightBlack(cls):
        return Fore.LIGHTBLACK_EX

theme = Theme()