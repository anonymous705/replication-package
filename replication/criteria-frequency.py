import os
import csv
from concurrent.futures import ThreadPoolExecutor
import sys


def classify_technology_in_directory(repo_path):
    """
    Classify the technology based on files in the repository directory.
    Priority: Pulumi > Terraform > AWS CDK
    """
    for root, _, files in os.walk(repo_path):
        for f in files:
            if f.endswith("Pulumi.yaml") or f.endswith("Pulumi.yml"):
                return "Pulumi"
            elif f.endswith("cdktf.json") or f.endswith(".tf"):
                return "Terraform"
            elif f.endswith("cdk.json"):
                return "AWS CDK"
            elif f.endswith(".edn"):
                return "NUBANK"
    return "NOTFOUND"


def process_criteria(criteria_dir, output_dir):
    """
    Process a single criteria directory to classify technologies.
    """
    technology_counts = {"Pulumi": 0, "Terraform": 0, "AWS CDK": 0, "NUBANK": 0, "NOTFOUND": 0}
    results = []

    # Iterate over the subdirectories in the criteria directory
    for repo_id in os.listdir(criteria_dir):
        repo_path = os.path.join(criteria_dir, repo_id)

        # Only process if it's a directory
        if os.path.isdir(repo_path):
            tech_classification = classify_technology_in_directory(repo_path)
            technology_counts[tech_classification] += 1
            results.append([repo_id, tech_classification])

    # Write results to a CSV
    output_csv = os.path.join(output_dir, f"{os.path.basename(criteria_dir.rstrip('/'))}_output.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_csv, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Technology"])
        writer.writerows(results)

    # Print counts
    string = f"Counts for {criteria_dir}:\n"
    for tech, count in technology_counts.items():
        string += f"{tech}: {count}\n"
    print(string)
    
    return output_csv


def process_directories_in_parallel(criteria_dirs, output_dir):
    """
    Process all criteria directories in parallel.
    """
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_criteria, criteria_dir, output_dir)
            for criteria_dir in criteria_dirs
        ]
        for future in futures:
            print(f"Output CSV generated: {future.result()}")


if __name__ == "__main__":
    if not '--input' in sys.argv or not '--output' in sys.argv:
        print("Usage: python3 criterias-frequency.py --input path1,path2,path3,path4 --output path")
        sys.exit(1)

    criteria_dirs = [os.path.abspath(path) for path in sys.argv[sys.argv.index('--input') + 1].split(',')]
    print(f"Executing the frequency of the following paths: {criteria_dirs}")
    output_dir = os.path.abspath(sys.argv[sys.argv.index('--output') + 1])

    process_directories_in_parallel(criteria_dirs, output_dir)
