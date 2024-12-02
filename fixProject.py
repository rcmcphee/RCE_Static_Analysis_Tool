import json
import os
import re
import xml.etree.ElementTree as ET

def clean_data(value):
    """
    Recursively clean binary data from JSON values.
    """
    if isinstance(value, str):
        # Remove non-UTF-8 characters or replace them
        return value.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    elif isinstance(value, list):
        return [clean_data(item) for item in value]
    elif isinstance(value, dict):
        return {key: clean_data(val) for key, val in value.items()}
    else:
        return value  # Leave other types untouched
        

def preprocess_json(file_path):
    """
    Read the file in binary mode and strip any leading binary data.
    """
    try:
        with open(file_path, "rb") as binary_file:
            raw_data = binary_file.read()
        
        # Remove non-UTF-8 characters by decoding and replacing errors
        cleaned_data = raw_data.decode("utf-8", errors="replace")
        
        # Locate the start of the JSON object
        json_start = cleaned_data.find("{")
        if json_start == -1:
            raise ValueError("No JSON object found in the file.")
        
        # Trim to the start of the JSON object
        cleaned_data = cleaned_data[json_start:]
        
        return cleaned_data
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        raise


    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        # Load the JSON file
        print("Loading JSON...")
        with open(file_path, "r", encoding="utf-8") as infile:
            data = json.load(infile)
        print("JSON loaded successfully.")

        # Clean the data
        print("Cleaning data...")
        cleaned_data = clean_data(data)

        # Save the cleaned data to a new file
        print("Saving cleaned JSON...")
        with open(output_path, "w", encoding="utf-8") as outfile:
            json.dump(cleaned_data, outfile, ensure_ascii=False, indent=4)

        print(f"Binary data removed and saved to {output_path}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Raise the exception to diagnose issues


# Update Maven pom.xml
def update_pom(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    namespaces = {'maven': 'http://maven.apache.org/POM/4.0.0'}

    # Add JAXB dependencies
    dependencies = root.find('maven:dependencies', namespaces)
    if dependencies is None:
        dependencies = ET.SubElement(root, 'dependencies')

    jaxb_dependency = ET.SubElement(dependencies, 'dependency')
    ET.SubElement(jaxb_dependency, 'groupId').text = 'javax.xml.bind'
    ET.SubElement(jaxb_dependency, 'artifactId').text = 'jaxb-api'
    ET.SubElement(jaxb_dependency, 'version').text = '2.3.1'

    # Update compiler plugin configuration
    build = root.find('maven:build', namespaces)
    if build is None:
        build = ET.SubElement(root, 'build')
    
    plugins = build.find('maven:plugins', namespaces)
    if plugins is None:
        plugins = ET.SubElement(build, 'plugins')

    compiler_plugin = next((plugin for plugin in plugins.findall('maven:plugin', namespaces)
                            if plugin.find('maven:artifactId', namespaces).text == 'maven-compiler-plugin'), None)
    if compiler_plugin is None:
        compiler_plugin = ET.SubElement(plugins, 'plugin')
        ET.SubElement(compiler_plugin, 'artifactId').text = 'maven-compiler-plugin'

    configuration = compiler_plugin.find('maven:configuration', namespaces)
    if configuration is None:
        configuration = ET.SubElement(compiler_plugin, 'configuration')

    release = configuration.find('release')
    if release is None:
        release = ET.SubElement(configuration, 'release')
    release.text = '8'

    # Save the updated pom.xml
    tree.write(pom_path)
    print(f"Updated {pom_path} with JAXB dependencies and compiler settings.")

# Replace deprecated APIs
def replace_deprecated_apis(src_dir):
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()

                # Replace sun.misc.Unsafe occurrences (example)
                updated_content = content.replace('sun.misc.Unsafe', 'java.util.concurrent.atomic.AtomicInteger')

                if content != updated_content:
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    print(f"Updated deprecated APIs in {file_path}")

# # Paths
# project_dir = '/path/to/your/project'
# pom_path = os.path.join(project_dir, 'pom.xml')
# src_dir = os.path.join(project_dir, 'src/main/java')

# # Execute fixes
# update_pom(pom_path)
# replace_deprecated_apis(src_dir)
