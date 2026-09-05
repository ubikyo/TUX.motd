import subprocess

from datetime import datetime

from tux_motd.misc.module import Module
from tux_motd.misc.i18n import _, _n, col
from tux_motd.misc.ui import Display
from tux_motd.misc.theme import theme

class User(Module):

    settings = {}

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        """ Affiche les utilisateurs connectés """

        users = []

        result = subprocess.run(
            [
                "loginctl", 
                "list-sessions", 
                "--no-legend"
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        sessions = result.stdout.strip().splitlines()

        for line in sessions:
            if not line.strip():
                continue
            
            session_id = line.split()[0]

            result = subprocess.run(
                [
                    "loginctl", 
                    "show-session", 
                    session_id, 
                    "-p", 
                    "Name", 
                    "-p", 
                    "RemoteHost", 
                    "-p", 
                    "Timestamp"
                ], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            props = result.stdout.strip().splitlines()

            props_dict = {}
            for prop in props:
                if "=" in prop:
                    key, value = prop.split("=", 1)
                    props_dict[key] = value

            users.append({
                "user": props_dict.get("Name"),
                "host": props_dict.get("RemoteHost") or _("Local"),
                "since": datetime.strptime(props_dict.get("Timestamp"), "%a %Y-%m-%d %H:%M:%S %Z")
            })

        users = sorted(users, key=lambda x: x["host"], reverse=True)

        if users:
            Display.header(
                f"{_n('User', 'Users', len(users)):22}" +
                f"{_('From'):44}" +
                col("Since", len(f"Since")) +
                f"{_('At')}"
            )

            for user in users:
                print(
                    f"   {theme.Bright}{theme.Highlight}{self.get('icon','')}  " +
                    f"{user['user']:16}{theme.Reset}" +
                    f"{user['host']:44}" +
                    col(user["since"].strftime(_("Since_DateFormat")), None, "Since") +
                    f"{user['since'].strftime(_('At_DateFormat'))}\r"
                )