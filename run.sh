# Initialize location of the results folder
OUTPUT_DIR=$(pwd)"/results"

# Directory path for codeql
DIR="$HOME/codeql"

if [ -f "$DIR/codeql/codeql" ]; then
    codeql_executable="$DIR/codeql/codeql.exe"
else
    codeql_executable="$DIR/codeql/codeql.exe"
fi

# Enter Admin mode
# net session > /dev/null 2>&1
# if [ $? -ne 0 ]; then
#     echo "This script requires administrative privileges."
#     echo "Restarting with elevated privileges..."
#     # Re-run the script with elevated privileges
#     powershell -Command "Start-Process 'C:\Program Files\Git\bin\bash.exe' -ArgumentList '$0' -Verb runAs"
#     exit
# fi

# Get scanning options
while true; do
    # Get user input for single or list of repositories
    echo "Select an option:"
    echo "1) Scan a single repository"
    echo "2) Scan a list of repositories"
    echo "3) Scan random repositories"
    read -rp "Enter your choice: " mySCAN
    mySCAN=$(echo $mySCAN | tr -cd "[:alnum:]_.-")

    # Create output folder
    mkdir -p "$OUTPUT_DIR"

    # Make sure the user put either "1" or "2" if not, restart the loop to try again
    if [[ "$mySCAN" != "1" && "$mySCAN" != "2" && "$mySCAN" != "3" ]]; then
        echo "Invalid response, please try again"
    else
        while true; do
            # User entered "1"
            if [[ "${mySCAN}" == [1] ]]; then

                # Get user input for single repository URL
                read -rp "Enter repository URL: " myREPO_URL

                # Check to make sure URL is valid, if not, restart the loop to try again
                if ! git ls-remote "$myREPO_URL" &> /dev/null; then
                    echo "$myREPO_URL is an invalid URL, please try again"
                else
                    
                    # Run the analysis tool with the repo URL and false for file
                    python -c "import repo; repo.cloneAndTraverse('$myREPO_URL', 'false', '$codeql_executable')" 
                    echo "Successful analysis performed"
                    break;
                fi

            # User entered "2"
            elif [[ "${mySCAN}" == [2] ]]; then
                # Get user input for filepath holding list of repositories
                read -rp "Enter list filepath: " myLIST_PATH

                # Check to make sure file exists and is readable, if not, restart the loop to try again
                if [ ! -r "$myLIST_PATH" ]; then
                    echo "Invalid filename/path, please try again"
                else

                    # Run the analysis tool with the filepath and true for file
                    python repo.py myLIST_PATH true
                    echo "Successful analysis performed"
                    break
                fi

            # User entered "3"
            elif [[ "${mySCAN}" == [3] ]]; then
                # Get user input for number of repositories scanned
                read -rp "Enter desired number of repositories to scan: " numREPOS

                if [[ "${numREPOS}" =~ ^[0-9]+$ ]] && [ "$numREPOS" -gt 0 ]; then
                    python -c "import randomRepo; import json; result = randomRepo.randomReposInit($((numREPOS))); print(json.dumps(result, indent=4))" > output.json
                    # Loop through each Maven project entry in output.json
                    cat output.json | jq -c '.[]' | while read -r artifact; do
                        # Extract the relevant fields using jq
                        group=$(echo "$artifact" | jq -r '.a')
                        artifact_name=$(echo "$artifact" | jq -r '.a')
                        version=$(echo "$artifact" | jq -r '.latestVersion')
                        pom_url=$(echo "$artifact" | jq -r '.pom')

                        # Print the project details for debugging
                        echo "Processing project: $group:$artifact_name:$version"

                        # Download the POM file (if necessary)
                        pom_file="./$artifact_name.pom"
                        curl -s -o "$pom_file" "$pom_url"

                        # Check if the POM file was downloaded successfully
                        if [[ ! -f "$pom_file" ]]; then
                            echo "Failed to download POM file for $group:$artifact_name:$version. Skipping..."
                            continue
                        fi

                        # Assume the repository URL is provided in the JSON (adjust if needed)
                        # The URL in this case is the JAR file URL
                        if [[ -n "$jar_url" ]]; then
                            # Download the JAR file
                            jar_file="./$artifact_name-$version.jar"
                            echo "Downloading JAR file from: $jar_url"
                            curl -L -o "$jar_file" "$jar_url"

                            # Check if the JAR file was downloaded successfully
                            if [[ ! -f "$jar_file" ]]; then
                                echo "Failed to download JAR file for $group:$artifact_name:$version. Skipping..."
                                continue
                            fi
                        fi

                        # Run CodeQL analysis using the Python script
                        echo "Running CodeQL analysis on repository $repo_name"

                        # Run the analysis tool with the repo URL and false for file
                        python -c "import repo; repo.cloneAndTraverse('$repo_name', '$repo_url', 'false', '$codeql_executable')" 
                        echo "Successful analysis performed"
                    done
                else
                    echo "Invalid input. Please enter a number greater than 0."
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