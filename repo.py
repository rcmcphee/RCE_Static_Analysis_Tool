import subprocess
import sys
import os


# Function to extract .jar file
def extract_jar(jar_file):
    subprocess.run(["jar", "-xvf", jar_file], check=True, shell=True)

# Function to check if any .java files exist in the directory
def has_java_files():
    return any(file.endswith(".java") for file in os.listdir(os.getcwd()))

# Function to clone and traverse through the given repository
def cloneProject(jar_url, codeql_path):

    # Set MAVEN_OPTS for the current environment
    os.environ["MAVEN_OPTS"] = "--add-opens java.base/java.lang=ALL-UNNAMED"
    # os.environ["JAVA_TOOL_OPTIONS"] = "--add-opens java.base/java.lang=ALL-UNNAMED"
    
    # Extract Maven coordinates from URL
    try:
        # Assuming the URL points directly to the .jar file
        parts = jar_url.split("/")
        artifact_id = parts[-2]  # Example: "spring"
        version = parts[-1].replace(".jar", "")  # Example: "1.0.2"

        # Print basic information
        print(f"Processing JAR file for artifact ID: {artifact_id}, version: {version}")

        # Create working directory
        working_dir = f"codeql-analysis-{artifact_id}-{version}"
        os.makedirs(working_dir, exist_ok=True)
        os.chdir(working_dir)

        # Download the JAR file
        jar_file = f"{version}.jar"

        print(jar_file)

        print(f"Downloading JAR file from {jar_url}...")
        subprocess.run(["curl", "-s", "-O", jar_url], check=True, shell=True)

        if not os.path.exists(jar_file):
            print(f"Error: Failed to download JAR file from {jar_url}")
            sys.exit(1)

        # Initialize CodeQL database
        print("Initializing CodeQL database...")
        database_name = f"codeql-database-{artifact_id}-{version}"

        # Extract the .jar contents
        # extract_jar(jar_file)

        subprocess.run([codeql_path, "database", "create", database_name, "--language=java", "--command", 
                        f"jar xf {jar_file}"], check=True, shell=True)

        # # Check if any Java files were extracted
        # if has_java_files():
        #     # If .java files are found, create a CodeQL database from the extracted Java files
        #     print("Creating CodeQL database from extracted Java files...")
        #     subprocess.run([codeql_path, "database", "create", f"codeql-database-{jar_file}",
        #                     "--language=java", "--command", "javac -d . *.java"], check=True, shell=True)
        # else:
        #     # If no Java files are found, create CodeQL database from the JAR (bytecode analysis)
        #     print("No Java source files found. Running bytecode analysis on JAR file...")
        #     subprocess.run([codeql_path, 'database', 'create', f'codeql-database-{jar_file}', 
        #                     '--language=java', '--command', f'java -jar {jar_file}'], check=True, shell=True)


        # Run CodeQL analysis
        print("Running CodeQL analysis...")
        subprocess.run([codeql_path, "database", "analyze", f"codeql-database-{jar_file}",
                        "codeql/java-queries/ql/src/codeql-suites/java-security-and-quality.qls", "--format=sarifv2.1.0",
                        "--output", f"{jar_file}.sarif"], check=True, shell=True)

        print(f"CodeQL analysis complete. Results saved to {jar_file}.sarif")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)