#!/bin/bash

# Function to log messages
log_init() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${BASH_SOURCE[0]}.log"
}

# Function to backup the file for safety
backup_file() {
    local file="$1"
    if [ -f "$file" ] && [ ! -f "${file}.bak" ]; then
        cp "$file" "${file}.bak"
        log_init "Backed up $file to ${file}.bak."
    fi
}

# Function to create a file if it doesn't exist
create_file_if_not_exists() {
    local file="$1"
    if [ ! -f "$file" ]; then
        touch "$file"
        log_init "Created $file as it did not exist."
    fi
}

# Function for wsl.conf in /etc
setup_wsl_conf() {
    backup_file /etc/wsl.conf
    log_init "Setting up the /etc/wsl.conf file with bash customizations..."
    
    cat << 'EOF' > /etc/wsl.conf
[boot]
systemd=true

[network]
generateResolvConf = true
EOF

    log_init "Set up the /etc/wsl.conf as below:"
    cat /etc/wsl.conf
}

# Function to set up aliases
setup_aliases() {
    create_file_if_not_exists ~/.bash_aliases
    backup_file ~/.bash_aliases
    log_init "Setting up the .bash_aliases file with all aliases..."

    cat << 'EOF' > ~/.bash_aliases
echo Greetings $USER from ${BASH_SOURCE[0]}

alias ..='cd ..'
alias a='alias'
alias countfiles='find -maxdepth 1 -type d | sort | while read -r dir; do n=$(find "$dir" -type f | wc -l); printf "%4d : %s\n" $n "$dir"; done'
alias diskspace='du -ahc --time . -d 1 | sort -h -r'
alias duah='du -ah -d 1 $1 | sort -hr'
alias e='exit'
alias emptyfoldercountfiles='find -maxdepth 1 -type d | sort | while read -r dir; do n=$(find "$dir" | wc -l); let n--; if [ $n -eq 0 ]; then printf "%4d : %s\n" $n "$dir"; fi; done'
alias exportdisplay='export DISPLAY=:0.0'
alias filescount='find . -maxdepth 1 -type d | while read -r dir; do printf "%s:\t" "$dir"; find "$dir" -type f | wc -l; done'
alias hostname='uname -n'
alias install='sudo apt-get install --install-suggests --show-progress $*'
alias javaprocs='pwdx $(pgrep java)'
alias l='ls -CF'
alias la='ls -A'
alias ll='ls -alF'
alias lsa='ls -ld .?*'
alias lsblk='lsblk -afm --output=VENDOR,NAME,FSTYPE,KNAME,LABEL,SERIAL,UUID,SIZE,STATE,OWNER,GROUP,MODE'
alias lsla='ls -la'
alias lslha='ls -lha'
alias lsltha='ls -ltha'
alias mci='mvn clean install -Dmaven.test.skip $*'
alias nonemptyfoldercontentcountfiles='find -maxdepth 1 -type d | sort | while read -r dir; do n=$(find "$dir" | wc -l); let n--; if [ $n -gt 0 ]; then printf "%4d : %s\n" $n "$dir"; fi; done'
alias nonzerocountifles='find -maxdepth 1 -type d | sort | while read -r dir; do n=$(find "$dir" -type f | wc -l); if [ $n -gt 0 ]; then printf "%4d : %s\n" $n "$dir"; fi; done'
alias nonzerosubfoldercountfiles='find -maxdepth 1 -type d | sort | while read -r dir; do n=$(find "$dir" -type d | wc -l); let n--; if [ $n -gt 0 ]; then printf "%4d : %s\n" $n "$dir"; fi; done'
alias nodename='uname --nodename'
alias os='cat /etc/os-release'
alias pd='pushd $*'
alias po='popd $*'
alias reload='source ~/.bashrc; source ~/.bash_profile'
alias subfoldercountfiles='find -maxdepth 1 -type d | sort | while read -r dir; do n=$(find "$dir" -type d | wc -l); let n--; printf "%4d : %s\n" $n "$dir"; done'
alias systeminfo='uname -a'
alias update='sudo apt-get update'
alias upgrade='sudo apt-get upgrade -y'

alias kubectl='kubectl.exe'
alias kubens='kubens.exe'
alias helm='helm.exe'
alias fzf='fzf.exe'
alias k9s='k9s.exe'
alias kai='kubectl-ai.exe'

# Set the alias loaded flag
export ALIASES_LOADED=true
EOF

    log_init "Aliases set up in .bash_aliases."
}

# Function to set up custom bash configurations
setup_bashrc_custom() {
    create_file_if_not_exists ~/.bashrc_custom
    backup_file ~/.bashrc_custom
    log_init "Setting up the .bashrc_custom file with customizations of bashrc..."

    cat << 'EOF' > ~/.bashrc_custom
echo Greetings $USER from ${BASH_SOURCE[0]}

# Load custom aliases if not already loaded
if [ -z "$ALIASES_LOADED" ] && [ -f "$HOME/.bash_aliases" ]; then
    . "$HOME/.bash_aliases"
fi

export CLOUDSDK_PYTHON_SITEPACKAGES=1

gcm() { grep -rin $1 * ; }
gcmd() { grep -rn $1 * | head -1 ; }

ge(){
    filepathlinux=$(dos_path_to_linux "$@")
    echo $filepathlinux
    gedit $filepathlinux & disown
}
startserver(){
    python -m SimpleHTTPServer $1
}
dirsize() {
    du -ahc --time -d 1 $@ | sort -hr;
}
dos_path_to_linux(){
    sed -e 's?\\?/?g' -e 's?[cC]:?/mnt/c?' <<<"$@"
}
function cd {
    builtin cd "$@" && ls -F
}
mkcd () {
    mkdir -p -- "$1" && cd -P -- "$1"
}
aptcleanup(){
    sudo apt-get update
    sudo apt-get clean
    sudo apt-get autoremove
    sudo apt-get update && sudo apt-get upgrade
    sudo apt-get install -f
    sudo dpkg --configure -a
}
cdls() { 
    cd "$@" && ls; 
}

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${BASH_SOURCE[0]}.log"
}

# Function to check if the dependency utilities are available else exit the script
check_command() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "Command $1 is not installed. Exiting."
        exit 1
    }
}

# Function to give single line utility to run command and log message before that and in case of error echo error message
log_and_check() {
    local cmd="$1"
    local log_msg="$2"
    local error_msg="$3"

    echo "$log_msg"
    if ! eval "$cmd"; then
        log_init "$error_msg"
        echo "$error_msg"
        exit 1
    fi
}
EOF

    log_init "Custom bash configurations set up in .bashrc_custom."
}

# Function to set up .bash_profile to set up the bash profile configurations and customizations
setup_bash_profile() {
    create_file_if_not_exists ~/.bash_profile
    backup_file ~/.bash_profile
    log_init "Setting up the .bash_profile file with bash specific profile changes..."

    cat << 'EOF' > ~/.bash_profile
echo Greetings $USER from ${BASH_SOURCE[0]}

# Source the .profile file for general settings
if [ -f ~/.profile ]; then
    . ~/.profile
fi

# Commented out loading of .bashrc since we are sure it is already done
# if running bash, include .bashrc if not already included by .profile
# if [ -n "$BASH_VERSION" ] && [ -z "$BASHRC_LOADED" ]; then
#     if [ -f "$HOME/.bashrc" ]; then
#         . "$HOME/.bashrc"
#         export BASHRC_LOADED=true
#     fi
# fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Load custom configurations
if [ -f "$HOME/.bashrc_custom" ]; then
    . "$HOME/.bashrc_custom"
fi

# PS1='${debian_chroot:+($debian_chroot)}\[\033[01;36m\]\u\[\033[00m\]@\[\033[01;36m\]\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
PS1="\[\e[01;36m\]\u\[\e[0;34m\][]\[\e[1;32m\]\h"
PS1="$PS1\[\e[01;31m\]@\[\e[0;33m\]\D{%Y%m%d_%H%M%S}"
PS1="$PS1 \[\e[1;33m\]\W\\$\[\e[m\] "
export PS1

#sudo visudo -c

git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager.exe"

EOF

    log_init "Configured .bash_profile to load profile, bashrc_custom, and other configurations."
}

# Function to create Always Run as Sudo Script file which can be used to add any code that will always run in admin mode
setup_always_as_sudo() {
    log_init "Setting up the always_as_sudo file which will run all its commands as sudo..."

    cat << 'EOF' > always_as_sudo
#!/usr/bin/sudo bash
echo "$(whoami) - $(id -u)"
# below command on top of script will enable as root
[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"

#==========================================================

#!/bin/bash
# To know current user or id (0 for root)
# id -u
# echo "$(whoami)"
EOF

    chmod +x always_as_sudo
    log_init "Configured the always_as_sudo file with skeleton code which will always run as sudo."
}

# Function to create run script file that will run the script and will show output as well as log output in a file in a generic way
setup_run_script() {
    log_init "Setting up the run_script file which will run the script and also show the output on the console with error..."

    cat << EOF > run_script
exec > >(tee -a "log-\$1.log") 2>&1
# exec|(tee -a "${BASH_SOURCE[0]}.log") 2>&1
# exec > >(tee -a "${BASH_SOURCE[0]}.log") 2>&1
# exec>> ${BASH_SOURCE[0]}.log 2>&1
echo Running the \$1
bash \$1
echo Completed run of \$1
# cat "${BASH_SOURCE[0]}.log"
EOF

    chmod +x run_script
    log_init "Configured the run_script file which will run the script and also show the output on the console with error."
}

# Main script execution
main() {
    log_init "Script execution started..."

    setup_wsl_conf
    setup_aliases
    setup_bashrc_custom
    setup_bash_profile
    setup_always_as_sudo
    setup_run_script

    log_init "Script execution completed."
}

# Execute main function
main

source ~/.bash_profile
