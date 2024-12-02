import os
import random
import subprocess
from urllib.parse import urlparse
import requests

from repoGit import cloneCreateAnalyze

# Perform GitHub API calls to get random repository URLs with specified parameters
def getReposRandom():
    # Define the base GitHub search query
    query = "language:java size:<10000"

    # Define range of keywords to get different projects on each query
    parameters = ["spring framework", "java", "react", "api", "data science", "machine learning", "spring boot", "mysql", "sqlite"]
    random_parameter = random.choice(parameters)
    
    # Randomly select a page number to ensure different results on each call
    page_number = random.randint(1, 20)
    
    # Create the URL with the query and page number
    url = f"https://api.github.com/search/repositories?q={random_parameter} {query}&page={page_number}&per_page=10"
    
    # Send a GET request to the GitHub API
    return requests.get(url)

# Receive individual GitHub repository URL and send to the analysis program
def individualRepo(passed_url, output_dir, decoded_output_dir):
    parsed_url = urlparse(passed_url)
    # Split the path and get the last part, which is the repo name
    name = parsed_url.path.strip('/').split('/')[-1]
    db_path = name + "-db"
    try:
        cloneCreateAnalyze(name, passed_url, db_path, output_dir, decoded_output_dir)
    except Exception as e:
        print(f"Issue with {passed_url} due to error: {e}")
        raise

# MAIN METHOD
# Retrieve GitHub API call and loop through to preform functions on each. Keep track of already processed repos 
# how close the sample size the program is
def scanSetup(numRepos, passed_url, list_path):
    output_dir_name = "query_results"
    decoded_output_dir_name = "query_decoded_results"

    if os.path.exists(output_dir_name):
        subprocess.run(["rm", "-rf", output_dir_name], check=True)
    os.mkdir(output_dir_name)

    if os.path.exists(decoded_output_dir_name):
        subprocess.run(["rm", "-rf", decoded_output_dir_name], check=True)
    os.mkdir(decoded_output_dir_name)

    output_dir = os.path.join(os.getcwd(), output_dir_name)
    decoded_output_dir = os.path.join(os.getcwd(), decoded_output_dir_name)

    if numRepos == -1:
        try:
            individualRepo(passed_url, output_dir, decoded_output_dir)
        except Exception as e:
            print(f"Issue with {passed_url} due to error: {e}")
            raise

    elif numRepos == 0:
        try:
            # Open the file for reading
            with open(list_path, 'r') as file:
                # Iterate through each line in the file
                for line in file:
                    # Strip any leading/trailing whitespace and print the URL
                    try:
                        individualRepo(line, output_dir, decoded_output_dir)
                    except Exception as e:
                        print(f"Issue with {passed_url} due to error: {e}")
                        raise
        except FileNotFoundError:
            print(f"Error: The file '{list_path}' was not found.")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    elif numRepos > 0:
        scannedRepos = []
        while numRepos > 0:
            # Get random repos
            response = getReposRandom()

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                repositories = data["items"]

                # Print the repository names and their sizes
                for repo in repositories:
                    name = repo["name"]
                    repos_url = repo["html_url"]

                    git_url = repos_url + ".git"
                    db_path = name + "-db"

                    if git_url not in scannedRepos:
                        try:
                            cloneCreateAnalyze(name, git_url, db_path, output_dir, decoded_output_dir)
                            numRepos -= 1
                            scannedRepos.append(git_url)
                        except Exception as e:
                            print(f"Skipping repository {git_url} due to error: {e}")
            else:
                print(f"Error: {response.status_code}")

        with open("repos.txt", "w") as file:
            for repo in scannedRepos:
                file.write(f"{repo}\n")
