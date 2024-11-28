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

# Enter Admin mode
net session > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "This script requires administrative privileges."
    echo "Restarting with elevated privileges..."
    # Re-run the script with elevated privileges
    powershell -Command "Start-Process 'C:\Program Files\Git\bin\bash.exe' -ArgumentList '$0' -Verb runAs"
    exit
fi

# Check if python/pip is installed
if command -v python &> /dev/null && command -v pip &> /dev/null; then
    echo "Python/PIP already installed"
else
    winget install --id Python.Python.3 
    echo "Python/PIP successfully installed"
fi

choco install jq

# Update pip if needed
python.exe -m pip install --upgrade pip

# Install code dependencies
pip install --upgrade GitPython
python -m pip install javalang
pip install --upgrade import-java
pip install --upgrade requests
pip install --upgrade pywin32

# Initialize location of the results folder
OUTPUT_DIR=$(pwd)"/results"

# Directory path for codeql
DIR="$HOME/codeql"

# Clean PATH for duplicates
# Deduplicate PATH
export PATH=$(echo "$PATH" | awk -v RS=':' '!seen[$0]++' | tr '\n' ':' | sed 's/:$//')

# Save changes to ~/.bash_profile
sed -i '/export PATH/d' ~/.bash_profile
echo "export PATH=\"$PATH\"" >> ~/.bash_profile

# Apply changes
source ~/.bash_profile

# Confirm result
echo "Cleaned PATH: $PATH"

# Check for Java installation
if command -v java &> /dev/null; then
    echo "JAVA_HOME is already set correctly: $JAVA_HOME"
else
    if [ -z "$JAVA_HOME" ]; then
        echo "JAVA_HOME is not set. Attempting to auto-detect..."
        
        JAVA_BIN=$(which java 2>/dev/null)
        if [ -n "$JAVA_BIN" ]; then
            JAVA_HOME=$(dirname "$(dirname "$JAVA_BIN")")
            echo "Auto-detected JAVA_HOME: $JAVA_HOME"
        else
            echo "Java not found. Installing OpenJDK..."

            # Install OpenJDK
            JDK_VERSION="23"
            JDK_VERSION_FULL="23.0.1"
            JDK_URL="https://download.oracle.com/java/${JDK_VERSION}/latest/jdk-${JDK_VERSION}_windows-x64_bin.zip"
            JDK_INSTALL_DIR="$HOME/jdk-${JDK_VERSION_FULL}"
            
            # Create install directory
            mkdir -p "$JDK_INSTALL_DIR"

            echo "Downloading OpenJDK from $JDK_URL..."
            if curl -L "$JDK_URL" -o "$HOME/openjdk.zip"; then
                unzip -qo "$HOME/openjdk.zip" -d "$HOME" || { echo "Failed to extract OpenJDK"; exit 1; }
                rm "$HOME/openjdk.zip"
            else
                echo "Failed to download OpenJDK. Check your internet connection or the URL."
                exit 1
            fi

            JAVA_HOME="$JDK_INSTALL_DIR"
            export JAVA_HOME
            export PATH="$JAVA_HOME/bin:$PATH"
            echo "Installed OpenJDK at: $JAVA_HOME"
        fi
    fi

    # Source the updated .bash_profile to apply changes
    echo "export PATH=\"$JAVA_HOME/bin:\$PATH\"" >> ~/.bash_profile
    export PATH="$JAVA_HOME/bin:$PATH"

    source ~/.bash_profile

    # Verify installation
    if [ -x "$JAVA_HOME/bin/java" ]; then
        echo "JAVA_HOME set to: $JAVA_HOME"
        java -version
    else
        echo "Error: JAVA_HOME is not set correctly. Please check your Java installation."
        exit 1
    fi
fi



# Check for Maven installation and install if missing
if command -v mvn &> /dev/null; then
    echo "Maven is already installed"
else
    # Go into administrator mode for download
    echo "Maven not found. Installing Maven..."

    # Define Maven version and URL
    # URL: "https://downloads.apache.org/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.zip"
    MAVEN_VERSION="3.9.9"
    MAVEN_URL="https://downloads.apache.org/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.zip"
    MAVEN_DIR="$HOME/apache-maven"

    # Download Maven, ensure URL is correct
    echo "Downloading Maven from $MAVEN_URL"
    curl -L "$MAVEN_URL" -o "$HOME/maven.zip" || { echo "Failed to download Maven"; exit 1; }

    # Check if the downloaded file is a valid zip file
    if ! unzip -tq "$HOME/maven.zip" &> /dev/null; then
        echo "The downloaded file is not a valid zip file or the download failed. Please check your network connection and try again."
        exit 1
    fi

    # Extract the Maven zip file
    unzip -qo "$HOME/maven.zip" -d "$HOME" || { echo "Failed to extract Maven"; exit 1; }
    rm "$HOME/maven.zip"

    # Add Maven to PATH
    MAVEN_DIR=$(find "$HOME" -type d -name "apache-maven*" | head -n 1)
    echo "export PATH=\"$MAVEN_DIR/bin:\$PATH\"" >> ~/.bash_profile
    export PATH="$MAVEN_DIR/bin:$PATH"

    # Reload to apply changes
    source ~/.bash_profile

    echo "Maven installed successfully!"
    echo "Maven version: " 
    mvn -version
else
    echo "Maven already installed"
fi

# Check for codeql installation
if [ -f "$DIR/codeql/codeql" ] || [ -f "$DIR/codeql/codeql.exe" ]; then
    echo "CodeQL installed; Version:"
    
    # Determine the correct executable path
    if [ -f "$DIR/codeql/codeql" ]; then
        codeql_executable="$DIR/codeql/codeql.exe"
    else
        codeql_executable="$DIR/codeql/codeql.exe"
    fi

    # Run CodeQL version check using the determined executable path
    "$codeql_executable" --version
else
    # Go into administrator mode for download
    net session > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "This script requires administrative privileges."
        echo "Restarting with elevated privileges..."
        # Re-run the script with elevated privileges
        powershell -Command "Start-Process 'C:\Program Files\Git\bin\bash.exe' -ArgumentList '$0' -Verb runAs"
        exit
    fi

    # Ensure curl is installed and available to be used
    if ! command -v curl &> /dev/null; then
        winget install --id curl.curl -e || { echo "Failed to install curl"; exit 1; }
    fi

    # Ensure unzip is installed and available to be used
    if ! command -v unzip &> /dev/null; then
        winget install -e --id 7zip.7zip -e || { echo "Failed to install 7zip"; exit 1; }
    fi
    
    # Install CodeQL via https://github.com/github/codeql-cli-binaries/releases/download/v2.19.3/codeql-win64.zip
    CQL_VERSION="2.19.3"
    CQL_URL="https://github.com/github/codeql-cli-binaries/releases/download/v${CQL_VERSION}/codeql-win64.zip"
    DOWNLOAD_DIR="$HOME/tmp/codeql_download"

    # Make temporary CodeQL directory
    mkdir -p "$DOWNLOAD_DIR" "$DIR"

    # Download and Extract CodeQL CLI
    curl -L "$CQL_URL" -o "$DOWNLOAD_DIR/codeql.zip" || { echo "Failed to download CodeQL"; exit 1; }
    unzip -qo "$DOWNLOAD_DIR/codeql.zip" -d "$DIR" || { echo "Failed to extract CodeQL"; exit 1; }

    # Ensure binaries are not restricted
    chmod -R ugo+rwx "$DIR"

    # Add CodeQL to path
    export PATH="$DIR/codeql:$PATH"

    # Cleanup
    rm -rf "$DOWNLOAD_DIR"

    # Reload to apply changes
    source ~/.bash_profile
fi

# Get current location
CURRENT_DIR=$(pwd)

# Start a new Git Bash instance and navigate to the current directory
start "" "C:\Program Files\Git\git-bash.exe" --login -i -c "cd '$CURRENT_DIR' && exec bash"

# Close the current window
exit