from git import Repo
import os

# Obtain the location of the current directory for copying
CONST_DIRECTORY = os.getcwd()

# Function to clone and traverse through the given repository
def cloneAndTraverse(repoURL):
    # Clone the passed repository into the current directory
    repo = Repo.clone_from(repoURL, CONST_DIRECTORY)

    # Get the tree of files in the repository
    tree = repo.head.commit.tree

    # Traverse through the tree of files
    for blob in tree.traverse():
        if blob.type == 'blob':
            try:
                # Extract the contents of each file
                data = blob.data_stream.read().decode('utf-8', errors='ignore')
                # Send to analysis function
                analyze(data)
            # Error check incase of a failure to read file
            except Exception as e:
                print(f"Cannot analyze {blob.path}: {e}")

# Analyze the contents of the file for RCE vulnerabilities
def analyze(contents):
    exit