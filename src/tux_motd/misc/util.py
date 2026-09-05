import os
import shutil

from tux_motd.misc.configuration import Configuration

def get_size(value):
    """ 
        Donne la taille en octet avec la meilleure unité
        Args:
            value (int): La valeur en octet.
        Returns:
            str: La valeur retournée (ex. 10Mo).
    """       

    for unit in Configuration.get("graph.units",["o","Ko","Mo","Go","To","Po"]):
        if value < 1024:
            if unit in Configuration.get("arround.units",["o","Ko","Mo"]):
                return f"{int(value)}{unit}"
            else:
                return f"{value:.2f}{unit}"
        value /= 1024
    return f"{value:.2f}Po"

def strip_ansi(text):
    """ 
        Supprime les caractères unicodes (couleur / style) 
        Args:
            text (str): La texte à modifier.
        Returns:
            str: Le texte modifié.
    """       

    import re
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)

def has_command(cmd):
    """ 
        Vérifie si une commande est disponible
        Args:
            cmd (str): Le nom de la commande.
        Returns:
            bool: True si la commande est disponible, sinon False.
    """
    return shutil.which(cmd) is not None

def is_root():
    """ 
        Vérifie si l"utilisateur courant est root
        Returns:
            bool: True si l"utilisateur est root, sinon False.
    """
    return os.geteuid() == 0

def clean_screen():
    print("\033[2J\033[H", end="")