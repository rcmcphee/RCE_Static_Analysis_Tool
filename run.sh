# Get scanning options
while true; do
    # Get user input for single or list of repositories
    echo "Select an option:"
    echo "1) Scan a single repository"
    echo "2) Scan a list of repositories"
    echo "3) Scan random repositories"
    read -rp "Enter your choice: " mySCAN
    mySCAN=$(echo $mySCAN | tr -cd "[:alnum:]_.-")

    # Make sure the user put either "1" or "2" if not, restart the loop to try again
    if [[ "$mySCAN" != "1" && "$mySCAN" != "2" && "$mySCAN" != "3" ]]; then
        echo "Invalid response, please try again"
    else
        while true; do
            # User entered "1"
            if [[ "${mySCAN}" == [1] ]]; then

                read -rp "Enter the URL of the GitHub Repository: " git_url

                # Validate the URL format
                if [[ ! $git_url =~ ^https?://.*\.git$ ]]; then
                    echo "Invalid URL. Please provide a valid .jar file URL starting with http:// or https://."
                    exit 1
                fi

                # Pass the URL to the Python script
                numREPOS=-1
                python -c "import randomRepoGit;  randomRepoGit.scanSetup($numREPOS, '$git_url', '$list_path')"
                break;

            # User entered "2"
            elif [[ "${mySCAN}" == [2] ]]; then
                # Get user input for filepath holding list of repositories
                read -rp "Enter list filepath: " list_path

                # Check to make sure file exists and is readable, if not, restart the loop to try again
                if [ ! -r "$list_path" ]; then
                    echo "Invalid filename/path, please try again"
                else
                    numREPOS=0
                    python -c "import randomRepoGit;  randomRepoGit.scanSetup($numREPOS, '$git_url', '$list_path')"
                    break
                fi

            # User entered "3"
            elif [[ "${mySCAN}" == [3] ]]; then
                # Get user input for number of repositories scanned
                read -rp "Enter desired number of repositories to scan: " numREPOS

                if [[ "${numREPOS}" =~ ^[0-9]+$ ]] && [ "$numREPOS" -gt 0 ]; then

                    python -c "import randomRepoGit;  randomRepoGit.scanSetup($numREPOS, '$git_url', '$list_path')"

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