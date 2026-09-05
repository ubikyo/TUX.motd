#!/bin/bash

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOTD_DIR="/etc/update-motd.d"

# Installation des packages python
install_requirements() {
    if $PYTHON3 -m pip install -r "$MODULE_DIR/requirements.txt" > /dev/null 2>tux_error.log; then
        set_success "MOTD" "Requirements installed successfully"
    else
        set_error "MOTD" "Failed to install requirements"
    fi
}

# Installation de la police figlet
install_font() {
    if pyfiglet -L "$MODULE_DIR/ressources/termius.flf" > /dev/null 2>tux_error.log; then
        set_success "MOTD" "Figlet font installed successfully"
    else
        set_error "MOTD" "Failed to install font"
    fi
}

# Créé la configuration de base
init_configuration() {
    if has_command systemctl; then
        print_msg "OK" "MOTD" "Configuration initialized"
        mkdir -p "/etc/TUX/"

        local input_file="$MODULE_DIR/ressources/tux_motd.services"
        local template_file="$MODULE_DIR/ressources/tux_motd.yaml"
        local output_file="/etc/TUX/tux_motd.yaml"

        local services_block=""

        while IFS=";" read -r name svc || [[ -n $name ]]; do
            [ -z "$svc" ] && continue

            if systemctl status "${svc}.service" &>/dev/null; then
                services_block+="        ${name}: ${svc}"$'\n'
            fi
        done < "$input_file"

        awk -v block="$services_block" '
        {
            if ($0 ~ /\{services\}/) {
                gsub(/\{services\}/, "")
                printf "%s", block
            } else {
                print
            }
        }
        ' "$template_file" > "$output_file"
    fi
}


# Compilation des packages python
build_module() {
    if $PYTHON3 -m pip install "$MODULE_DIR" > /dev/null 2>tux_error.log; then
        set_success "MOTD" "Module built successfully"
    else
        set_error "MOTD" "Failed to build module"
    fi
}

# Nettoyage des fichiers
clean_module() {
    if {
        $PYTHON3 setup.py clean --all &&
        rm -rf *.egg-info
        rm -rf __pycache__
    } > /dev/null 2>tux_error.log; then
        set_success "MOTD" "Module cleaned successfully"
    else
        set_error "MOTD" "Failed to cleaning module"
    fi
}

# Création d'un lien symbolique vers /usr/local/bin
link_module() {
    if print_dialog $SILENT "Create a symbolic link to tux_motd in /usr/local/bin ?"; then
        print_msg "OK" "MOTD" "Linking module to /usr/local/bin"
        ln -sf $VENV_DIR/bin/tux_motd /usr/local/bin/tux_motd
    else
        print_msg "INFO" "MOTD" "Skipping symbolic link creation"
    fi
}

disabled_motd() {
    if [ -d "$MOTD_DIR" ]; then
        if print_dialog $SILENT "Disable existing MOTD (like landscape)?"; then
            print_msg "OK" "MOTD" "Disabled all existing MOTD (/etc/update-motd.d/*)"
            chmod -x $MOTD_DIR/*
        else
            print_msg "INFO" "MOTD" "Skipping disabling existing MOTD"
        fi

        # Remove legal notice if exists
        rm /etc/legal

        # Suppress sudo message on first use
        touch ~/.sudo_as_admin_successful
    fi
} 

# Configure le MOTD
init_motd() {
    if [ ! -d "$MOTD_DIR" ]; then
        mkdir -p "$MOTD_DIR"
    fi

    print_msg "OK" "MOTD" "Initializing tux_motd configuration"
    tee $MOTD_DIR/99-tux-motd > /dev/null <<EOF
#!/bin/bash
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
tux_motd
EOF

    print_msg "OK" "MOTD" "Set execute permission to tux_motd"
    sudo chmod +x $MOTD_DIR/99-tux-motd
}

# Désactive l'affichage du dernier login
disabled_printlastlog() {
    if print_dialog $SILENT "Disable PrintLastLog in SSH config (requires script to restart SSH)?"; then

        local ssh_config_file="/etc/ssh/sshd_config"

        if [ -f "$ssh_config_file" ]; then
            local ssh_backup_file="$ssh_config_file.bak.$(date +%s)"

            cp "$ssh_config_file" "$ssh_backup_file"

            if grep -qE "^\s*#?\s*PrintLastLog\s+" "$ssh_config_file"; then
                sed -i 's/^\s*#\?\s*PrintLastLog\s\+.*/PrintLastLog no/' "$ssh_config_file"
            else
                echo "PrintLastLog no" >> "$ssh_backup_file"
            fi

            systemctl restart ssh

            if systemctl is-active --quiet ssh; then
                rm "$ssh_backup_file"
                set_success "MOTD" "PrintLastLog disabled successfully"
            else
                cp "$ssh_backup_file" "$ssh_backup_file"
                rm "$ssh_backup_file"
                systemctl restart ssh
                set_error "MOTD" "Failed to disabled PringLastLog revert to old configuration"
            fi
        fi
    else
        print_msg "INFO" "MOTD" "Skipping disabling PringLastLog"
    fi
}

main() {
    cd "$MODULE_DIR"

    print_header "Module Motd installation\n"

    install_requirements || { quit_installation; return; }
    install_font || { quit_installation; return; }
    build_module || { quit_installation; return; }
    clean_module || { quit_installation; return; }
    link_module
    disabled_motd
    init_motd
    init_configuration
    disabled_printlastlog || { quit_installation; return; }

    cd ..
}

main "$@"