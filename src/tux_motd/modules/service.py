import subprocess

from tux_motd.misc.module import Module
from tux_motd.misc.i18n import _, _n, col
from tux_motd.misc.ui import Display
from tux_motd.misc.theme import theme

class Service(Module):

    settings = {}

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        """ Affiche l"état de certaines services """

        services = (self.get("check", {})).items()

        if services:

            Display.header(
                f"{_n('Service', 'Services', len(services)):36}" +
                col("Running?", len(f"Running?")) +
                f"{_('Enabled?')}"
            )

            for name, service in services:

                if not name or not service:
                    continue

                state_yes = _("Yes")
                state_no  = _("No")

                if self.is_service(f"{service}.service", "is-active"):
                    run_status = state_yes
                    run_color  = theme.Ok
                else:
                    run_status = state_no
                    run_color  = theme.Critical

                if self.is_service(f"{service}.service", "is-enabled"):
                    boot_status = state_yes
                    boot_color  = theme.Ok
                else:
                    boot_status = state_no
                    boot_color  = theme.Critical

                print(
                    f"   {theme.Bright}{theme.Highlight}" +
                    f"{self.get('icon', '󰒔')}  " +
                    f"{name:30}{theme.Reset}" +
                    f"{run_color}" +
                    col(run_status, None, "Running?") +  
                    f"{boot_color}{boot_status}{theme.Reset}\r"
                )

    def is_service(self, service, state):
        """ 
            Vérifie l"état d"un service
            Args:
                service (str): Le nom du service.
                state (str): L"état à vérifier (is-active, is-enabled).
            Returns:
                bool: True si le service est dans l"état demandé, sinon False.
        """

        result = subprocess.run(["systemctl", state, "--quiet", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return result.returncode==0