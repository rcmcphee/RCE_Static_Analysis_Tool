import csv
import json
import subprocess
import os

from fixProject import preprocess_json, replace_deprecated_apis, update_pom

def run_codeql_db_creation(repo_url, db_path):

    # Remove any existing github repository in temporary location "repo"
    subprocess.run(["rm", "-rf", "repo"], check=True)

    # Clone the repository to temporary location "repo"
    subprocess.run(["git", "clone", repo_url, "repo"], check=True)

    # Create the CodeQL database
    try:
        # Remove any existing database directory with the same path
        subprocess.run(["rm", "-rf", db_path], check=True)

        # Attempt to run the CodeQL command
        subprocess.run(
            ["codeql", "database", "create", db_path, "--language=java", "--source-root=repo"],
            check=True
        )
        print("CodeQL database created successfully.")
    except subprocess.CalledProcessError as e:
        # Handle the failure
        print(f"CodeQL database creation failed with error: {e}")

        # Remove any existing database directory with the same path to clear after the error
        subprocess.run(["rm", "-rf", db_path], check=True)
        raise

def append_csv(file_to_append, target_file):
    # Open the file to append to in append mode ('a')
    with open(target_file, 'a', newline='', encoding='utf-8') as target:
        writer = csv.writer(target)
        
        # Open the file that contains the new data to be appended
        with open(file_to_append, 'r', newline='', encoding='utf-8') as source:
            reader = csv.reader(source)
            
            # Iterate through each row in the source file and write to the target file
            for row in reader:
                writer.writerow(row)

def decode_results(bqrs_path, csv_output_path):
    try:
        # Create base csv file off of the first bqrs file
        subprocess.run([
            "codeql", "bqrs", "decode",
            "--format=csv",
            "--output", csv_output_path,
            bqrs_path
        ], check=True)
        print(f"Results decoded and saved to {csv_output_path}")
    except Exception as e:
        print(f"Failed to decode results: {e}")
        raise

def decode_temp_results(bqrs_path, csv_output_path, temp_csv_output_path):
    try:
        # Create base csv file off of the first bqrs file
        subprocess.run([
            "codeql", "bqrs", "decode",
            "--format=csv",
            "--output", temp_csv_output_path,
            bqrs_path
        ], check=True)
        print(f"Results decoded and saved to {temp_csv_output_path}")
        append_csv(temp_csv_output_path, csv_output_path)
    except Exception as e:
        print(f"Failed to decode results: {e}")
        raise
    
   
def run_codeql_analysis(name, db_path, output_path, decoded_output_path):

    bqrs_output_file_name = name + "_results.bqrs"
    csv_output_file_name = name + "_results.csv"
    temp_csv_output_file_name = name + "_temp_results.csv"

    result_path = os.path.join(output_path, bqrs_output_file_name)
    decoded_path = os.path.join(decoded_output_path, csv_output_file_name)
    temp_decoded_path = os.path.join(decoded_output_path, temp_csv_output_file_name)
                                
    custom_query = "C:/Users/rcmcp/GitHub/RCE_Static_Analysis_Tool/custom_rce_query.qls"

    api_query = "C:/Users/rcmcp/codeql/codeql/qlpacks/codeql/java-queries/1.1.9/Security/CWE/CWE-020/ExternalAPIsUsedWithUntrustedData.ql"

    login_query = "C:/Users/rcmcp/codeql/codeql/qlpacks/codeql/java-queries/1.1.9/Security/CWE/CWE-117/LogInjection.ql"

    sql_query = "C:/Users/rcmcp/codeql/codeql/qlpacks/codeql/java-queries/1.1.9/Security/CWE/CWE-089/SqlConcatenated.ql"

    jndi_query = "C:/Users/rcmcp/codeql/codeql/qlpacks/codeql/java-queries/1.1.9/Security/CWE/CWE-074/JndiInjection.ql"

    ldap_query = "C:/Users/rcmcp/codeql/codeql/qlpacks/codeql/java-queries/1.1.9/Security/CWE/CWE-090/LdapInjection.ql"

    print(db_path)
    print(result_path)

    subprocess.run(["codeql", "query", "run", 
                    "--database", db_path, 
                    "--output", result_path,  # Specify output file name
                    api_query
    ], 
    capture_output=True, text=True, check=True)

    # Decodes and writes the api query to results.csv
    decode_results(result_path, decoded_path)

    subprocess.run(["codeql", "query", "run", 
                    "--database", db_path, 
                    "--output", result_path,  # Specify output file name
                    login_query
    ], 
    capture_output=True, text=True, check=True)

    # Decodes and writes the login query to the temp csv
    decode_temp_results(result_path, decoded_path, temp_decoded_path)

    subprocess.run(["codeql", "query", "run", 
                    "--database", db_path, 
                    "--output", result_path,  # Specify output file name
                    sql_query
    ], 
    capture_output=True, text=True, check=True)

    # Decodes and writes the login query to the temp csv
    decode_temp_results(result_path, decoded_path, temp_decoded_path)

    subprocess.run(["codeql", "query", "run", 
                    "--database", db_path, 
                    "--output", result_path,  # Specify output file name
                    jndi_query
    ], 
    capture_output=True, text=True, check=True)

    # Decodes and writes the login query to the temp csv
    decode_temp_results(result_path, decoded_path, temp_decoded_path)

    subprocess.run(["codeql", "query", "run", 
                    "--database", db_path, 
                    "--output", result_path,  # Specify output file name
                    ldap_query
    ], 
    capture_output=True, text=True, check=True)

    # Decodes and writes the login query to the temp csv
    decode_temp_results(result_path, decoded_path, temp_decoded_path)
    
    # Clean up
    subprocess.run(["rm", "-rf", "repo"], check=True)
    subprocess.run(["rm", temp_decoded_path], check=True)
    
def cloneCreateAnalyze(name, repo_url, db_path, output_path, decoded_output_path):

    try:
        run_codeql_db_creation(repo_url, db_path)
        try:
            run_codeql_analysis(name, db_path, output_path, decoded_output_path)

            # Remove database to help with storage
            subprocess.run(["rm", "-rf", db_path], check=True)

        except Exception as e:
            raise
    except Exception as e:
        raise

    
