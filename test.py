import glob
import subprocess
import sys
import os
import urllib.request
import shutil

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

# Function to find all .class files
def find_class_files(directory):
    return glob.glob(os.path.join(directory, '**', '*.class'), recursive=True)

# Function to set up a new directory for bytecode analysis
def setup_analysis_directory(class_files, analysis_dir):
    try:
        print(f"Setting up analysis directory: {analysis_dir}")
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Copy .class files to the analysis directory
        for class_file in class_files:
            shutil.copy(class_file, analysis_dir)
        print(f"Copied {len(class_files)} .class files to {analysis_dir}")
        
        # Change to the analysis directory
        os.chdir(analysis_dir)
    except Exception as e:
        print(f"Error setting up analysis directory: {e}")
        sys.exit(1)

# Function to create a CodeQL database
def create_codeql_database_from_class(database_path):
    print(os.getcwd())
    try:
        print(f"Creating CodeQL database in {database_path}...")
        # result = subprocess.run(["codeql", "database", "create", database_path,
        #                          "--language=java",
        #                          "--command", "java -cp . -Xmx4g -Duser.language=en -Duser.country=US"],
        #                         cwd=os.getcwd(),
        #                         capture_output=True, text=True, shell=True)
        subprocess.run(["codeql", "database", "create", database_path,
                        "--language=java",
                        "--source-root", "C:/Users/rcmcp/GitHub/RCE_Static_Analysis_Tool/codeql-analysis",
                        "--extract-only",
                        "--command", "cmd.exe /C echo Extracting source"
                    ], capture_output=True, text=True, shell=True)
        # if result.returncode != 0:
        #     try:
        #         print("Try with no main")
        #         subprocess.run(["codeql", "database", "create", database_path,
        #             "--language=java",
        #             "--source-root", "C:/Users/rcmcp/GitHub/RCE_Static_Analysis_Tool/codeql-analysis/org/springframework",
        #             "--extractor-option", "java --compile-only"],
        #             capture_output=True, text=True, shell=True)
        #     except subprocess.CalledProcessError as e:
        #         print(f"Error creating CodeQL database: {result.stderr}")
        #         sys.exit(1)

        print(f"CodeQL database created successfully: {database_path}")

        # Finalize the database
        print(f"Finalizing database")
        result = subprocess.run(["codeql", "database", "finalize", database_path],
                                capture_output=True, text=True, shell=True)
        
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")


    except subprocess.CalledProcessError as e:
        print(f"Error creating CodeQL database: {e}")
        sys.exit(1)


# Function to run CodeQL analysis on the database
def run_codeql_analysis(database_path, results_file):
    try:
        print(f"Running CodeQL analysis for {database_path}...")
        result = subprocess.run(["codeql", "database", "analyze", database_path,
                                 "--format=sarifv2.1.0", "--output", results_file],
                                capture_output=True, text=True, shell=True)
        
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")

        if result.returncode != 0:
            print(f"Error during CodeQL analysis: {result.stderr}")
            sys.exit(1)
        print(f"CodeQL analysis complete. Results saved to {results_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during CodeQL analysis: {e}")
        sys.exit(1)

# Main function to analyze the JAR file
def analyze_jar(jar_url, results_file="results.sarif"):
    # Define the working directory for analysis
    working_dir = os.path.abspath("codeql-analysis")
    os.makedirs(working_dir, exist_ok=True)
    os.chdir(working_dir)

    # Extract artifact name and version
    parts = jar_url.split("/")
    artifact_id = parts[-2]  # Extract artifact ID
    version = parts[-1].replace(".jar", "")  # Extract version

    # Set the database path within the working directory
    database_path = os.path.join(working_dir, f"codeql-database-{artifact_id}-{version}")

    # Download the JAR file
    jar_file = f"{version}.jar"
    download_jar(jar_url, jar_file)

    # Extract the JAR file contents
    extract_jar(jar_file)

    # Find .class files
    class_files = find_class_files(os.getcwd())
    if class_files:
        print(f"Found {len(class_files)} .class files.")
        
        # # Create a new directory for analysis and move into it
        # analysis_dir = os.path.join(working_dir, "bytecode-analysis")
        # setup_analysis_directory(class_files, analysis_dir)
        
        # Create a CodeQL database
        create_codeql_database_from_class(database_path)
    else:
        print(f"No .class files found. Cannot proceed with analysis.")
        sys.exit(1)

    # Run CodeQL analysis
    run_codeql_analysis(database_path, results_file)

# Example usage
# analyze_jar('https://repo.maven.apache.org/maven2/spring/spring/1.0.2/spring-1.0.2.jar')
