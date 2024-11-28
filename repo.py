import shutil
import subprocess

import requests
import analyze
import os
import win32api
import win32con
from git import Repo

# Obtain the location of the current directory for copying
CONST_DIRECTORY = os.getcwd()

# Create holder for list of java files in the repo
repo_files_java = []

# Function to clone and traverse through the given repository
def cloneAndTraverse(repo_name, file_name, artifact_name, version, repo_url, codeql_path):
    
    # Ensure current directory isn't deleted
    if repo_name == "":
        repo_name = "test"

    REPO_DIRECTORY = CONST_DIRECTORY + "\\" + file_name

    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        with open(repo_url, "wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download POM file for {repo_name}: {e}. Skipping...")
        exit()

    # Step 2: Set Java options and run Maven to get dependencies
    os.environ["JAVA_OPTS"] = "--add-opens java.base/java.lang=ALL-UNNAMED"

    try:
        subprocess.run(
            ["mvn", "dependency:get", f"-Dartifact={repo_name}", "-U"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to run Maven for {repo_name}: {e}. Skipping...")
        exit()

    # Step 3: Check if the JAR file was downloaded successfully
    jar_file = f"./{artifact_name}-{version}.jar"
    if not os.path.isfile(jar_file):
        print(f"Failed to download JAR file for {repo_name}. Skipping...")
        exit()

    # Clear any existing directories
    if os.path.exists(REPO_DIRECTORY):
        shutil.rmtree(REPO_DIRECTORY, onerror=force_delete_readonly)

    analyze.codeql_Java(repo_name, REPO_DIRECTORY, codeql_path)

    # Delete the cloned repo for future use
    shutil.rmtree(REPO_DIRECTORY, onerror=force_delete_readonly)

# Remove read-only priviledge from files for use in deleting GitHub Repos
def force_delete_readonly(func, path, exc_info):
    win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_NORMAL)
    func(path)
