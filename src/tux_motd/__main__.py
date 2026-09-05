#!/usr/bin/env python3

import importlib

from colorama import init

from tux_motd.misc.i18n import setup_translation
from tux_motd.misc.util import clean_screen
from tux_motd.misc.ui import Display
from tux_motd.misc.configuration import Configuration

def get_modules():
    modules = []

    try:
        for module in Configuration.get("modules", []):
            module_name, settings = next(iter(module.items()))
            order = settings.get("position", 1000)
            content = settings.get('content')

            if content is not None:
                for idx, item in enumerate(content):
                    method_name, method_settings = next(iter(item.items()))
                    if method_settings == None: method_settings = {}
                    if method_settings == {} or method_settings.get("show", True):
                        modules.append({
                            "order": order,
                            "module_name": module_name,
                            "idx": idx,
                            "method_name": method_name,
                            "settings": {**settings, **method_settings},
                        })
            else:
                if settings.get("show", True):
                    modules.append({
                        "order": order,
                        "module_name": module_name,
                        "idx": 0,
                        "method_name": None,
                        "settings": settings,
                    })

        modules.sort(key=lambda module: (module["order"], module["idx"]))

        return modules
    
    except AttributeError:
        Display.error(f"Module error \"{module_name}\", incorrect indent ?")
        return []
    except Exception as e:
        Display.error(f"Module error \"{module_name}\" : {e}")
        return []


def start_modules():
    for module in get_modules():
        try:
            module_name = module["module_name"]
            method_name = module["method_name"]

            mod = importlib.import_module(f"tux_motd.modules.{module_name}")

            class_name = module_name.capitalize()
            cls = getattr(mod, class_name, None)

            if cls and hasattr(cls, "init_module"):
                instance = cls(module["settings"])
                if method_name:
                    method = getattr(instance, method_name, None)
                    if callable(method):
                        method()
                    else:
                        Display.error(f"Method {method_name} not found in {class_name}")
                else:
                    instance.run()

        except Exception as e:
           Display.error(f"Instantiation error of module {module_name} : {e}")

def main():
    clean_screen()

    Configuration.load("/etc/TUX/tux_motd.yaml")

    setup_translation(Configuration.get("language","en"))

    start_modules()

    print("\n\n")

if __name__ == "__main__":
    main()