import shutil
import stat
import analyze
import os
from git import Repo

# Obtain the location of the current directory for copying
CONST_DIRECTORY = os.getcwd()

# Create holder for list of java files in the repo
repo_files_java = []

# Function to clone and traverse through the given repository
def cloneAndTraverse(repoURL, isList):

    # Clear any existing directory
    shutil.rmtree(CONST_DIRECTORY + "/tempDirectory", onerror=remove_readonly)
    
    # Clone the passed repository into the current directory
    repo = Repo.clone_from(repoURL, CONST_DIRECTORY + "/testDirectory")

    # Get the tree of files in the repository
    tree = repo.head.commit.tree

    # Populate Java file array
    createJavaList(tree)

    # Perform analysis on all files
    for file in repo_files_java:
        analyze.java(file)

    # Delete the cloned repo for future use
    shutil.rmtree(CONST_DIRECTORY + "/tempDirectory", onerror=remove_readonly)

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
def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)
