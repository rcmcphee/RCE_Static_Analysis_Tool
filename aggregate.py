import os
import pandas as pd

# Initialize the overall statistics to solve errors.
def initialize_overall_stats():
    return {
        "ExternalAPI": {"total_entries": 0, "unique_entries": set()},
        "LogInjection": {"total_entries": 0, "unique_entries": set()},
        "SQLConcatenation": {"total_entries": 0, "unique_entries": set()},
        "JNDIInjection": {"total_entries": 0, "unique_entries": set()},
        "LDAPInjection": {"total_entries": 0, "unique_entries": set()},
        "Files": 0,
    }

# Parse CSV file into sections based on header lines of an empty file
def parse_csv_sections(file_path):
    sections = {}
    current_section = None
    data = []

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            # Detect section headers
            if line in [
                '"externalApi","numberOfUses","numberOfUntrustedSources"',
                "col0,source,sink,col3,col4,col5",
                "query,col1,uncontrolled,col3",
            ]:
                # Save the previous section
                if current_section and data:
                    try:
                        sections[current_section] = pd.DataFrame(
                            data, columns=["externalApi", "numberOfUses", "numberOfUntrustedSources"]
                        )
                    except Exception as e:
                        print(f"Error creating DataFrame for section {current_section}: {e}")
                # Start a new section
                current_section = {
                    '"externalApi","numberOfUses","numberOfUntrustedSources"': "ExternalAPI",
                    "col0,source,sink,col3,col4,col5": "LogInjection",
                    "query,col1,uncontrolled,col3": "SQLConcatenation",
                }[line]
                data = []
            elif current_section:
                # Process rows for the current section
                try:
                    parts = line.split(",")
                    if len(parts) >= 3:
                        # Properly formatted row
                        data.append(parts[:3])
                    else:
                        # Handle malformed row: take everything before the first comma as `externalApi`
                        externalApi = parts[0] if parts else "MALFORMED"
                        data.append([externalApi, 1, 1])  # Default values for missing columns
                        print(f"Handled malformed row in {current_section}: {line}")
                except Exception as e:
                    print(f"Error processing row in {current_section}: {line}, Error: {e}")

        # Save the last section
        if current_section and data:
            try:
                sections[current_section] = pd.DataFrame(
                    data, columns=["externalApi", "numberOfUses", "numberOfUntrustedSources"]
                )
            except Exception as e:
                print(f"Error creating DataFrame for section {current_section}: {e}")

    return sections

# Process single CSV file; Update overall statistics accordingly
def process_csv_file_with_sections(file_path, overall_stats):    
    print(f"Processing file: {file_path}")
    sections = parse_csv_sections(file_path)

    has_vulnerability = False

    file_results = {"filename": file_path, "results": {}}

    for section, df in sections.items():
        if not df.empty and "externalApi" in df.columns:
            # Group by the 'externalApi' column to count occurrences
            grouped_data = df.groupby("externalApi").size().reset_index(name="count")
            file_results["results"][section] = {"data": df, "total_per_category": grouped_data}

            # Update overall statistics
            overall_stats[section]["total_entries"] += len(df)
            overall_stats[section]["unique_entries"].update(df["externalApi"].unique())

            if len(df) > 0:
                has_vulnerability = True
        else:
            # Handle cases where the section is empty or missing expected columns
            print(f"Skipping section {section} in file {file_path} due to missing or empty data.")
            file_results["results"][section] = {"data": pd.DataFrame(), "total_per_category": pd.DataFrame()}

    if has_vulnerability:
        overall_stats["Files"] += 1

    return file_results

# Finalize overall statistics to solve errors --> convert unique entry sets to counts.
def finalize_overall_stats(overall_stats):    
    for section in overall_stats:
        overall_stats[section]["unique_entries"] = len(overall_stats[section]["unique_entries"])

# Save processed results to a file with overall statistics.
def save_results_to_file(results, output_file, overall_stats):   
    with open(output_file, 'w') as f:
        # Write overall statistics
        f.write("Overall Statistics:\n")

        # Sum total entries for all sections, excluding non-section keys like 'Files'
        total_entries = sum(stats["total_entries"] for key, stats in overall_stats.items() if key != "Files")
        f.write(f"  Total Entries Across All Files: {total_entries}\n")

        for section, stats in overall_stats.items():
            if section != "Files":  # Avoid trying to access dictionary fields for the "Files" scalar
                f.write(f"  Total {section} entries across all files: {stats['total_entries']}\n")
                f.write(f"  Unique {section} entries across all files: {stats['unique_entries']}\n")

        # Add the total number of files with any vulnerability
        f.write(f"  Total Files with Any Vulnerability: {overall_stats['Files']}\n")
        f.write("\n")

        # Write per-file results
        for result in results:
            f.write(f"File: {result['filename']}\n")
            f.write("  Per-Section Statistics for this file:\n")
            for section, stats in result["results"].items():
                f.write(f"    {section}:\n")
                if not stats["data"].empty:
                    f.write(stats["data"].to_csv(index=False))
                else:
                    f.write("      No entries found.\n")
                f.write("\n")

# Process all .csv files in the specified folder and save results to a specified file.
def process_csv_folder_with_sections(folder_path, output_file):
    results = []
    overall_stats = initialize_overall_stats()

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            result = process_csv_file_with_sections(file_path, overall_stats)
            results.append(result)

    save_results_to_file(results, output_file, overall_stats)
    print(f"Results saved to {output_file}")

# MAIN METHOD
# Specify folder path and output file
folder_path = r"C:/Users/rcmcp/GitHub/RCE_Static_Analysis_Tool/saveResults"
output_file = r"C:/Users/rcmcp/GitHub/RCE_Static_Analysis_Tool/analysis_results.txt"

# Preset statistics for error resolution
overall_stats = initialize_overall_stats()

# Run processing 
process_csv_folder_with_sections(folder_path, output_file)
