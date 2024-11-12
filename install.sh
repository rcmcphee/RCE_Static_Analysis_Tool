#!/usr/bin/env bash

myINSTALLER=$(cat << "EOF"

    ____  ____________   _____ __        __  _         ___                __           _         ______            __
   / __ \/ ____/ ____/  / ___// /_____ _/ /_(_)____   /   |  ____  ____ _/ /_  _______(_)____   /_  __/___  ____  / /
  / /_/ / /   / __/     \__ \/ __/ __ `/ __/ / ___/  / /| | / __ \/ __ `/ / / / / ___/ / ___/    / / / __ \/ __ \/ / 
 / _, _/ /___/ /___    ___/ / /_/ /_/ / /_/ / /__   / ___ |/ / / / /_/ / / /_/ (__  ) (__  )    / / / /_/ / /_/ / /  
/_/ |_|\____/_____/   /____/\__/\__,_/\__/_/\___/  /_/  |_/_/ /_/\__,_/_/\__, /____/_/____/    /_/  \____/\____/_/   
                                                                        /____/                                       
EOF
)

# Start installation
echo "$myINSTALLER"
echo "Installing tool and required dependencies"

# Check if python/pip is installed
if command -v python &> /dev/null && command -v pip &> /dev/null; then
    echo "Python/PIP already installed"
else
    winget install --id Python.Python.3 
    echo "Python/PIP successfully installed"
fi

# Update pip if needed
python.exe -m pip install --upgrade pip

# Install code dependencies
pip install --upgrade GitPython
python -m pip install javalang
pip install --upgrade import-java
pip install --upgrade semgroup
pip install --upgrade requests

# Get scanning options
while true; do
    # Get user input for single or list of repositories
    read -rp "Scan single repository (1) or list of repositories (2)? " mySCAN
    mySCAN=$(echo $mySCAN | tr -cd "[:alnum:]_.-")

    # Make sure the user put either "1" or "2" if not, restart the loop to try again
    if [[ "$mySCAN" != "1" && "$mySCAN" != "2" ]]; then
        echo "Invalid response, please try again"
    else
        while true; do
            # User entered "1"
            if [[ "${mySCAN}" == [1] ]]; then

                # Get user input for single repository URL
                read -rp "Enter repository URL: " myREPO_URL
                myREPO_URL=$(echo "$myREPO_URL" | tr -cd "[:alnum:]_.-")

                # Check to make sure URL is valid, if not, restart the loop to try again
                if ! git ls-remote "$myREPO_URL" &> /dev/null; then
                    echo "Invalid URL, please try again"
                else
                    
                    # Run the analysis tool with the repo URL and false for file
                    python repo.py myREPO_URL false
                    echo "Successful analysis performed"
                    break;
                fi

            # User entered "2"
            elif [[ "${mySCAN}" == [2] ]]; then
                # Get user input for filepath holding list of repositories
                read -rp "Enter list filepath: " myLIST_PATH
                myLIST_PATH=$(echo $myLIST_PATH | tr -cd "[:alnum:]_.-")

                # Check to make sure file exists and is readable, if not, restart the loop to try again
                if [ ! -r "$myLIST_PATH" ]; then
                    echo "Invalid filename/path, please try again"
                else

                    # Run the analysis tool with the filepath and true for file
                    python repo.py myLIST_PATH true
                    echo "Successful analysis performed"
                    break
                fi

            # Failsafe incase user enters wrong input
            else
                echo "Error with user input"
                exit 1
            fi
        done
        break
    fi        
done
