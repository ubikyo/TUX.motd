# TUX.motd
Awesome MOTD for Ubuntu with system information and more.

> [!NOTE]
> Successfully tested on **Ubuntu 18** to **26+**.

<img src="https://raw.githubusercontent.com/ubikyo/TUX.motd/refs/heads/dev/ressources/motd.png" width="500">

# Prerequisites

TUX uses optional Nerd Fonts to display enhanced icons and symbols. To view these elements properly in your SSH terminal, you need to install a [Nerd Font](https://www.nerdfonts.com/font-downloads) (such as [Fira Code](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/FiraCode.zip), [DejaVuSans](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/DejaVuSansMono.zip), etc.) on your local machine. Nerd Fonts are standard fonts that have been patched to include over 10,000 icons from Font Awesome, Material Design, and more.

# Installation

Use the [TUX installation](https://github.com/ubikyo/TUX) to install TUX.motd.

# Debug

If the TUX.motd is not showing at login, edit **/etc/update-motd.d/99-tux-motd** and modify the relevant line as follows. Then logout and login again. Double-check the log at **/tmp/tuxmotd.log**

    tux_motd 2> /tmp/tuxmotd.log

# Developpment

## VENV

Activate the virtual environment (VENV).

    sudo -i
    cd /opt/TUX/repo/
    source ./scripts/venv-activate.sh
    cd modules/tux_motd/src/tux_motd

> [!WARNING]
> An interactive root session is required to access certain internal features.

## Edit

    nano src/tux_motd/__main__.py

## Start

    PYTHONPATH=src python -m tux_motd

## Build & dev

    python -m pip install -e .

## Install

    python -m pip install .

## Uninstall

    pip uninstall tux_motd -y

## Add a new language (ex. es aka spain)

    cd src/tux_motd/i18n/
    mkdir -p es/LC_MESSAGES
    cp en/LC_MESSAGES/messages.po es/LC_MESSAGES/
    cd es/LC_MESSAGES
    nano messages.po
    msgfmt -o messages.mo messages.po    

# Settings

The TUX.motd configuration can be found in the following file. All parameters are optional. The values provided below represent the default configuration.

    /etc/TUX/text.motd.yaml

## Language

    language: "fr"

> [!NOTE]
> Two languages are currently available: English (**en**) by default, and French (**fr**).
To add new languages, duplicate one of the existing language folders in the **i18n** directory and modify the **messages.po** file accordingly. Once your changes are complete, compile the file using the following command: **msgfmt -o messages.mo messages.po**

## Theme

    theme:
        hostname: "green"
        title: "white"
        ok: "green"
        warning: "magenta"
        critical: "red"
        highlight: "yellow"

> [!NOTE]
> The colors correspond to the colorama foreground values.

## Bargraph

    graph:
        width: 50
        symbol: "─"
        track_color: "black"

## Box

    box:
        width: 50
        color: "yellow"

## Modules

For each TUX.motb module, you can set the position and the display.

    modules: 
        - {module}
            position: 1
            show: true

> [!NOTE]
> See the default configuration on **/etc/TUX/text.motd.yaml** for usage of the different modules.

### Module Host

You can display all the content (hostname, distro, uptime, update) in one place with:

    - host:

Or, alternatively, content by content with:

    - host:
        content:
            - hostname:
                font: "termius"
            - distro:
                icon: ""
            - uptime:
                icon: ""
            - update:
                icon: "󰏓"
            - banner:
                message:
                    all: "Authorized personnel only. Or very sneaky cats."
                    ...
                    your_username: "Hi!"

> [!NOTE]
> You can use any default Fyglet font name.

> [!NOTE]
> Each **content** support **show** parameter.

### Module Processor

    - processor:
        icon:
            info : ""
            graph : ""

### Module Memory

    - memory:
        icon:
            info : ""
            graph: ""
        treshold:
            warn: 70
            critical: 90

### Module Disk

    - disk:
        exclude:
            - "/snap"
            - "/var/lib/snapd"
            - "/run/snapd"
            - "/System"
            - "/boot"
            ...
            - "/your_mount_point"
        icon:
            info : ""
            graph: ""
        treshold: 
            warn: 5
            critical: 10

### Module Service

    - service:
        icon: "󰒔"
        check:
            PHP FPM: php8.1-fpm
            Nginx: nginx
            MariaDB: mariadb
            UFW: ufw
            PostgreSQL: postgresql
            ...
            Your_Service_Name: your_service

### Module Network

You can display all the content (interface, route, resolver, firewall) in one place with:

    - network:
        ipv4: true
        ipv6: false
        exclude:
            - "lo"
            ...
            - "your_interface"

Or, alternatively, content by content with:

    - network:
        content:
            - interface:
                icon: "󱦂"    
            - route:
                icon: "󱇢"
            - resolver:
                icon: "󰖟"
            - firewall:
                icon: "󰕥"

> [!NOTE]
> Each **content** support **show** parameter.

### Module User
  
    - user:
        icon: ""