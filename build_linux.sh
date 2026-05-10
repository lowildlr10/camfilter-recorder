#!/usr/bin/env bash
set -e

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif command -v lsb_release &>/dev/null; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

install_system_deps() {
    local distro
    distro=$(detect_distro)

    case "$distro" in
        fedora | rhel | centos | rocky | almalinux)
            echo "Detected Fedora/RHEL-based distro ($distro)..."
            sudo dnf install -y python3-pip python3-virtualenv mesa-libGL glib2
            ;;
        debian | ubuntu | linuxmint | pop)
            echo "Detected Debian/Ubuntu-based distro ($distro)..."
            sudo apt-get update -qq
            sudo apt-get install -y python3-pip python3-venv libgl1 libglib2.0-0
            ;;
        arch | manjaro | endeavouros)
            echo "Detected Arch-based distro ($distro)..."
            sudo pacman -Sy --noconfirm python-pip mesa glib2
            ;;
        opensuse* | sles)
            echo "Detected openSUSE-based distro ($distro)..."
            sudo zypper install -y python3-pip python3-virtualenv libGL1 glib2-tools
            ;;
        *)
            echo "Warning: Unknown distro '$distro'. Skipping system package install."
            echo "Please ensure python3, pip, libGL, and glib2 are installed manually."
            ;;
    esac
}

install_system_deps

echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt
pip3 install --user pyinstaller

echo "Building standalone binary..."
pyinstaller \
  --onefile \
  --name "CamFilterRecorder" \
  main.py

chmod +x dist/CamFilterRecorder
echo ""
echo "Done! Run ./dist/CamFilterRecorder to launch the app."
