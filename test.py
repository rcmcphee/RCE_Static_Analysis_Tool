import glob
import subprocess
import sys
import os
import urllib.request

# Function to download the JAR file
def download_jar(jar_url, jar_file):
    try:
        print(f"Downloading JAR file from {jar_url}...")
        urllib.request.urlretrieve(jar_url, jar_file)
        print(f"JAR file downloaded successfully as {jar_file}")
    except Exception as e:
        print(f"Error downloading JAR file: {e}")
        sys.exit(1)

# Function to extract the JAR file
def extract_jar(jar_file):
    try:
        print(f"Extracting {jar_file}...")
        subprocess.run(["jar", "xf", jar_file], check=True)
        print(f"JAR file extracted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting JAR file: {e}")
        sys.exit(1)

def find_class_files(directory):
    # Use glob to find all .class files recursively
    return glob.glob(os.path.join(directory, '**', '*.class'), recursive=True)

# Function to create a CodeQL database from the extracted files (class files for bytecode analysis)
def create_codeql_database_from_class(codeql_path, database_name):
    try:
        print(f"Creating CodeQL database from extracted .class files for {database_name}...")
        # Ensure that the extracted files are in the current directory and create the database
        result = subprocess.run([codeql_path, "database", "create", database_name,
                 "--language=java", "--command", "java -cp . -Xmx4g -Duser.language=en -Duser.country=US"], 
                capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"Error creating CodeQL database: {result.stderr}")
            sys.exit(1)
        print(f"CodeQL database created successfully from .class files: {database_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating CodeQL database from class files: {e}")
        sys.exit(1)

# Function to run CodeQL analysis on the database
def run_codeql_analysis(codeql_path, database_name, results_file):
    try:
        print("Running CodeQL analysis...")
        result = subprocess.run([codeql_path, "database", "analyze", database_name, 
                                 "--queries=java-queries/ql/src/java-security-and-quality.qls", 
                                 "--format=sarifv2.1.0", "--output", results_file],
                                 capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            print(f"Error during CodeQL analysis: {result.stderr}")
            sys.exit(1)

        print(f"CodeQL analysis complete. Results saved to {results_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during CodeQL analysis: {e}")
        sys.exit(1)

# Main function to handle the JAR file analysis
def analyze_jar(jar_url, codeql_path, results_file="results.sarif"):
    # Define the working directory for analysis
    working_dir = "codeql-analysis"
    os.makedirs(working_dir, exist_ok=True)
    os.chdir(working_dir)

    # Extract the artifact name and version from the URL
    parts = jar_url.split("/")
    artifact_id = parts[-2]  # Extract artifact ID
    version = parts[-1].replace(".jar", "")  # Extract version

    # Set the name of the CodeQL database
    database_name = f"codeql-database-{artifact_id}-{version}"

    # Download the JAR file
    jar_file = f"{artifact_id}-{version}.jar"
    download_jar(jar_url, jar_file)

    # Extract the JAR file contents (should include .class files)
    extract_jar(jar_file)

    # Check if there are any .class files in the extracted contents
    class_files = find_class_files(os.getcwd())

    if class_files:
        # If there are .class files, create CodeQL database from them
        print(f"Found .class files")
        create_codeql_database_from_class(codeql_path, database_name)
    else:
        print(f"No .class files found in the extracted JAR file. Cannot create CodeQL database.")
        sys.exit(1)

    # Run CodeQL analysis
    run_codeql_analysis(codeql_path, database_name, results_file)

# Example usage
# analyze_jar('https://repo.maven.apache.org/maven2/spring/spring/1.0.2/spring-1.0.2.jar', '/path/to/codeql')
