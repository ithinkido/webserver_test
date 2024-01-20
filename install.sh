#!/bin/bash

dir="$HOME/webplotter"
venv="$HOME/penplotter_venv"
git="https://github.com/ithinkido/webserver_test.git"

#######################################################
#######################################################


spinner()
{
    local pid=$!
    local delay=1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}
printf "\033[?25l"

#System Info
lsb_release -ds
echo "$(getconf LONG_BIT)-bit OS"
python -V

BRANCH=$(lsb_release -cs)"_$(getconf LONG_BIT)"

if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed."
    return 1
else
    if [[ $(python3 -c 'import sys; print(sys.version_info >= (3, 9, 2))') == False ]]; then
        echo "Python version 3.9.2 or newer is required."
        return 1
    fi
fi

#get the curret debian version info
piversion=$(grep VERSION_ID /etc/os-release | cut -d '"' -f 2)
if [[ "$piversion" -lt 11 ]]; then
    echo "PiOS 11 (Bullseye) or newer is required."
    return 1
fi

echo ""
echo "Updating apt. This will take a while..."
(sudo apt-get update -qq > /dev/null) & spinner
wait


## Check for dir, if not found create it using the mkdir ##
if [ ! -d "$dir" ] ; then
    echo ""
    echo "Installing apt packages"
    (sudo apt-get install -qq -y git python3-pip libopenblas-dev libgeos-c1v5 libatlas-base-dev python3-venv libssl-dev > /dev/null) & spinner
    wait

    echo ""
    echo "Downloading Web Plotter from Github"
    if git ls-remote --exit-code --heads $git "$BRANCH" > /dev/null; then
        # DO NOT CHANGE without changing git actions 
        git clone -q -b "$BRANCH" $git "$dir" > /dev/null
    else
        echo "Branch does not exist"
        return 1
    fi
    wait
    echo ""

    echo "Create python venv"
    python3 -m venv $venv
    source $venv/bin/activate &&
    if [ -n "$VIRTUAL_ENV" ]; then
    echo "Pen plotter web server virtual environment is active."
    echo "Path: $VIRTUAL_ENV"
    else
        echo "Virtual environment is not active."
        return 1
    fi
    echo ""

    echo "Installing pip packages"
    (python3 -m pip install -q -r $dir/requirements.txt) & spinner
    wait
    echo ""
    
    echo "Preapre penplotter webserver config"
    cp $dir/config.ini.sample $dir/config.ini
    echo ""

    current_user=$(whoami)
    if [ "$current_user" != "pi" ]; then
        echo "Fix user define"
        echo "Setup user '$current_user' in webplotter.service" 
        sed -i "s/pi/$current_user/g" $dir/webplotter.service
        echo ""
    fi 

    echo "Setup auto start for Web Plotter on boot"
    echo ""
    sudo cp $dir/webplotter.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable webplotter > /dev/null
    sudo systemctl start webplotter
    echo ""

    sleep 2
    if sudo systemctl is-active --quiet webplotter; then
        IP_ADDRESS=$(hostname -I | awk '{print $1}')
        echo "After reboot - Web plotter can be found at http://$IP_ADDRESS:5000"
        echo ""
    else
        echo "Something has gone wrong...."
        cd $dir
        $venv/bin/python3 $dir/main.py &
        printf "\033[?25h"
        sleep 5
        exit 1
    fi

    printf "\033[?25h"
    printf "Rebooting in 5 sec "
    (for i in $(seq 4 -1 1); do
        sleep 1;
        printf ".";
    done;)
    echo ""
    echo ""
    echo "Rebooting"
    sleep 1
    sudo reboot


##########################################
###      UPDATE EXISTING INSTALL      ####
##########################################


else
    printf "\033[?25l"
    echo ""
    echo "Directory "$dir" already exists"
    echo ""
    mkdir -p temp
    if [ ! -d "$venv/" ]; then
        echo "Looks like you do not have a penplotter_venv virtual environment."
        echo "Let's take care of that."
        python3 -m venv $venv
        wait
    fi
    if [ -d "$dir/uploads/" ]; then
        mv "$dir/uploads/" temp/
    else
        echo "$dir/uploads/ does not exist. No files moved."
    fi
    if [ -e "$dir/config.ini" ]; then
        mv "$dir/config.ini" temp/
    else
        cp $dir/config.ini.sample temp/config.ini
    fi
    rm -rf "$dir"

    echo "Updating packages"
    if git ls-remote --exit-code --heads $git "$BRANCH" > /dev/null; then
        # DO NOT CHANGE without changing git actions 
        git clone -q -b "$BRANCH" $git "$dir" > /dev/null
    else
        echo "Branch does not exist"
        return 1
    fi
    wait    # add user files back
    
    rm -R $dir/uploads
    mv -f temp/* $dir/
    #clean up
    rm -R temp
    
    source $venv/bin/activate &&
    if [ -n "$VIRTUAL_ENV" ]; then
    echo "Pen plotter web server virtual environment is now active."
    echo "Path: $VIRTUAL_ENV"
    else
        echo "Virtual environment is not active."
        return 1
    fi
    echo ""

    python3 -m pip install -q --upgrade -r $dir/requirements.txt
    sudo rm -rf /etc/systemd/system/webplotter.service

    current_user=$(whoami)
    if [ "$current_user" != "pi" ]; then
        echo "Fix user define"
        echo "Setup user '$current_user' in webplotter.service" 
        sed -i "s/pi/$current_user/g" $dir/webplotter.service
        echo ""
    fi 

    sudo cp $dir/webplotter.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable webplotter
    sudo systemctl start webplotter

    sleep 2
    if sudo systemctl is-active --quiet webplotter; then
        IP_ADDRESS=$(hostname -I | awk '{print $1}')
        echo "After reboot - Web plotter can be found at http://$IP_ADDRESS:5000"
        echo ""
    else
        echo "Something has gone wrong...."
        source $venv/bin/activate &&
        cd $dir
        python3 $dir/main.py &
        printf "\033[?25h"
        sleep 5
        exit
    fi

    printf "\033[?25h"
    printf "Rebooting in 5 sec "
    (for i in $(seq 4 -1 1); do
        sleep 1;
        printf ".";
    done;)
    echo ""
    echo "Rebooting"
    sleep 1
    sudo reboot
fi