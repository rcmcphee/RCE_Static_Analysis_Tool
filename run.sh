# Initialize location of the results folder
OUTPUT_DIR=$(pwd)"/results"

# Directory path for codeql
DIR="$HOME/codeql"

if [ -f "$DIR/codeql/codeql" ]; then
    codeql_executable="$DIR/codeql/codeql.exe"
else
    codeql_executable="$DIR/codeql/codeql.exe"
fi

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

                # Input: POM file URL
                read -rp "Enter the .pom file URL: " pom_url

                # Extract group, artifact, and version from the URL
                IFS='/' read -ra URL_PARTS <<< "$pom_url"
                group_path="${URL_PARTS[-4]}"  # Group as a path (e.g., "org/springframework")
                artifact="${URL_PARTS[-3]}"    # Artifact name
                version="${URL_PARTS[-2]}"     # Version

                # Check if group_path is valid (some URLs may not follow the expected structure)
                if [[ -z "$group_path" || -z "$artifact" || -z "$version" ]]; then
                    echo "Error: Invalid .pom URL structure."
                    exit 1
                fi

                # Replace "/" in the group path with "." to form the group ID
                group_id="${group_path//\//.}"

                # Query Maven Central API
                query_url="https://search.maven.org/solrsearch/select?q=g:\"$group_id\"+AND+a:\"$artifact\"+AND+v:\"$version\"&rows=1&wt=json"
                echo "$query_url"
                
                response=$(curl -s "$query_url")

                # Check if the response is valid
                if echo "$response" | grep -q '"response":{"numFound":0'; then
                    echo "No results found for the given POM URL."
                else
                    echo "Project details retrieved successfully:"
                    echo "$response"  # Pretty print JSON response using jq
                fi

                group=$(echo "$response" | jq -r '.a')
                artifact_name=$(echo "$response" | jq -r '.a')
                version=$(echo "$response" | jq -r '.latestVersion')
                url=$(echo "$response" | jq -r '.jar')
                pom_url=$(echo "$response" | jq -r '.pom')

                repo_name=$group:$artifact_name:$version
                repo_file_name=$(echo "$repo_name" | sed 's/\./_/g')

                # Run the analysis tool with the repo URL and false for file
                echo "Processing project: $repo_name"
                python -c "import repo; repo.cloneAndTraverse('$repo_name', '$repo_file_name', '$artifact_name', '$version', '$pom_url', $codeql_executable')" 

                
                echo "Successful analysis performed"
                break;


            # # User entered "2"
            # elif [[ "${mySCAN}" == [2] ]]; then
            #     # Get user input for filepath holding list of repositories
            #     read -rp "Enter list filepath: " myLIST_PATH

            #     # Check to make sure file exists and is readable, if not, restart the loop to try again
            #     if [ ! -r "$myLIST_PATH" ]; then
            #         echo "Invalid filename/path, please try again"
            #     else

            #         # Run the analysis tool with the filepath and true for file
            #         python repo.py myLIST_PATH true
            #         echo "Successful analysis performed"
            #         break
            #     fi

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
                        url=$(echo "$artifact" | jq -r '.jar')
                        pom_url=$(echo "$artifact" | jq -r '.pom')
                    
                        repo_name=$group:$artifact_name:$version
                        repo_file_name=$(echo "$repo_name" | sed 's/\./_/g')
                        
                        # Print the project details for debugging
                        echo "Processing project: $repo_name"
                        python -c "import repo; repo.cloneAndTraverse('$repo_name', '$pom_url', $codeql_executable')" 

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