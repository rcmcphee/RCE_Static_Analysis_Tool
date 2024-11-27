import shutil
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
def cloneAndTraverse(repo_name, codeql_path):
    
    # Ensure current directory isn't deleted
    if repo_name == "":
        repo_name = "default"

    REPO_DIRECTORY = CONST_DIRECTORY + "\\" + repo_name

    # Clear any existing directories
    if os.path.exists(REPO_DIRECTORY):
        shutil.rmtree(REPO_DIRECTORY, onerror=force_delete_readonly)

    analyze.codeql_Java(repo_name, REPO_DIRECTORY, codeql_path)

    # Delete the cloned repo for future use
    shutil.rmtree(REPO_DIRECTORY, onerror=force_delete_readonly)

# Go through the repository and extract all files that end in ".java" for analysis                
def createJavaList(root, level=0):
    for entry in root:
        # Check if the file ends with ".java" and add it to the array of files if true
        if entry.name.endswith(".java"):
            repo_files_java.append(entry.path)
        # Recursively go through the folder if there are more 
        if entry.type == "tree":
            createJavaList(entry, level + 1)

# Remove read-only priviledge from files for use in deleting GitHub Repos
def force_delete_readonly(func, path, exc_info):
    win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_NORMAL)
    func(path)
