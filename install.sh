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
pip install GitPython


