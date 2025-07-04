#!/bin/bash
# VeriDoc Installation Script
# Installs VeriDoc CLI and shell completions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.local/bin"
COMPLETIONS_DIR="${HOME}/.local/share/bash-completion/completions"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    print_status "Found Python $python_version"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
        python3 -m pip install --user -r "${SCRIPT_DIR}/requirements.txt"
        print_success "Dependencies installed"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Install CLI script
install_cli() {
    print_status "Installing VeriDoc CLI..."
    
    # Create install directory if it doesn't exist
    mkdir -p "${INSTALL_DIR}"
    
    # Copy CLI script
    if [ -f "${SCRIPT_DIR}/veridoc" ]; then
        cp "${SCRIPT_DIR}/veridoc" "${INSTALL_DIR}/"
        chmod +x "${INSTALL_DIR}/veridoc"
        print_success "CLI installed to ${INSTALL_DIR}/veridoc"
    else
        print_error "veridoc CLI script not found"
        exit 1
    fi
    
    # Check if install directory is in PATH
    if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
        print_warning "${INSTALL_DIR} is not in your PATH"
        print_status "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "export PATH=\"\$PATH:${INSTALL_DIR}\""
    fi
}

# Install shell completions
install_completions() {
    print_status "Installing shell completions..."
    
    # Bash completion
    if command -v bash &> /dev/null; then
        local bash_completion_dir
        
        # Try different completion directories
        for dir in \
            "${HOME}/.local/share/bash-completion/completions" \
            "${HOME}/.bash_completion.d" \
            "/usr/local/etc/bash_completion.d" \
            "/etc/bash_completion.d"; do
            
            if [ -w "$(dirname "$dir")" ] || [ -w "$dir" ]; then
                bash_completion_dir="$dir"
                break
            fi
        done
        
        if [ -n "$bash_completion_dir" ]; then
            mkdir -p "$bash_completion_dir"
            if [ -f "${SCRIPT_DIR}/completions/bash_completion.sh" ]; then
                cp "${SCRIPT_DIR}/completions/bash_completion.sh" "${bash_completion_dir}/veridoc"
                print_success "Bash completion installed to ${bash_completion_dir}/veridoc"
            fi
        else
            print_warning "Could not find writable bash completion directory"
        fi
    fi
    
    # Zsh completion
    if command -v zsh &> /dev/null; then
        local zsh_completion_dir="${HOME}/.local/share/zsh/site-functions"
        
        if [ -f "${SCRIPT_DIR}/completions/zsh_completion.zsh" ]; then
            mkdir -p "$zsh_completion_dir"
            cp "${SCRIPT_DIR}/completions/zsh_completion.zsh" "${zsh_completion_dir}/_veridoc"
            print_success "Zsh completion installed to ${zsh_completion_dir}/_veridoc"
            print_status "Add this line to your ~/.zshrc if not already present:"
            echo "fpath=(~/.local/share/zsh/site-functions \$fpath)"
        fi
    fi
    
    # Fish completion
    if command -v fish &> /dev/null; then
        local fish_completion_dir="${HOME}/.config/fish/completions"
        
        if [ -f "${SCRIPT_DIR}/completions/fish_completion.fish" ]; then
            mkdir -p "$fish_completion_dir"
            cp "${SCRIPT_DIR}/completions/fish_completion.fish" "${fish_completion_dir}/veridoc.fish"
            print_success "Fish completion installed to ${fish_completion_dir}/veridoc.fish"
        fi
    fi
}

# Create desktop entry (optional)
install_desktop_entry() {
    local desktop_dir="${HOME}/.local/share/applications"
    local desktop_file="${desktop_dir}/veridoc.desktop"
    
    if [ ! -d "$desktop_dir" ]; then
        return
    fi
    
    print_status "Creating desktop entry..."
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Name=VeriDoc
Comment=AI-Optimized Documentation Browser
Exec=${INSTALL_DIR}/veridoc %F
Icon=text-x-generic
Terminal=false
Type=Application
Categories=Development;Documentation;
MimeType=text/markdown;text/plain;
EOF
    
    print_success "Desktop entry created"
}

# Main installation function
main() {
    echo "🚀 VeriDoc Installation Script"
    echo "=============================="
    echo
    
    # Check requirements
    check_python
    
    # Install components
    install_dependencies
    install_cli
    install_completions
    install_desktop_entry
    
    echo
    print_success "VeriDoc installation completed!"
    echo
    print_status "Quick start:"
    echo "  veridoc                    # Launch in current directory"
    echo "  veridoc README.md          # Open specific file"
    echo "  veridoc docs/              # Open specific directory"
    echo "  veridoc --help             # Show help"
    echo
    print_status "You may need to restart your shell or run 'source ~/.bashrc' for completions to work."
}

# Run installation
main "$@"