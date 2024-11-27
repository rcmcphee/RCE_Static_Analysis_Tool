import shutil
import subprocess
import os

# from buildProject import auto_detect_and_build

# Convert the bash unix path to windows path for subprocess
def convert(unix_path):
    if unix_path.startswith("/c/"):
        windows_path = "C:" + unix_path[2:].replace("/", "\\")
    else:
        # For other drives like /d/, /e/, etc.
        drive = unix_path[1:2].upper()  # Extract the drive letter
        windows_path = f"{drive}:\\{unix_path[3:].replace('/', '\\')}"
    
    return windows_path

# Analyze the contents of the file for RCE vulnerabilities
def codeql_Java(repo_Name, src_dir, codeql_path):

    # Print the file being analyzed
    codeql_path = convert(codeql_path)

    print(f"Converted codeql path: {codeql_path}")

    # Build project before execution
    # auto_detect_and_build(src_dir)

    db_dir = "./codeql-db"
    output_file = "./results/" + repo_Name + "_analysis_results.json"

    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)  # Clear existing database if exists

    # Create CodeQL database
    subprocess.run(
        [codeql_path, "database", "create", db_dir,
         "--language=java", f"--source-root={src_dir}", "--overwrite"], check=True
    )

    # Analyze the created database
    subprocess.run(
        [codeql_path, "database", "analyze", db_dir, "codeql/java-queries",
         "--format=json", "--output", output_file], check=True
    )