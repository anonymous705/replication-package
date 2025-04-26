#!/bin/bash

log_file="criterias.log"
default_dir="dataset"
python_cmd="python3"

function usage() {
  echo "Usage: $0 [-d directory] [-p python_interpreter]"
  echo "Options:"
  echo "  -d  Specify the directory of the repositories cloned (default: dataset)"
  echo "  -p  Specify the Python interpreter (default: python3)"
  exit 1
}

while getopts "d:p:" opt; do
  case "$opt" in
    d) target_dir="$OPTARG" ;;
    p) python_cmd="$OPTARG" ;;
    *) usage ;;
  esac
done

if [[ -z "$target_dir" ]]; then
  target_dir="$default_dir"
fi

echo "Execution of the apply criterias script started" > $log_file

function handle_error() {
  echo "[ERROR] $1. Exiting." | tee -a $log_file
  exit 1
}

mkdir -p csv/criterias-output || handle_error "Failed to create CSV directories"

echo "Creating criterias directories..." | tee -a $log_file
mkdir -p criterias/criteria1 criterias/criteria2 criterias/criteria3 criterias/criteria4 || handle_error "Failed to create criterias directories"

echo "Running the first filtering process..." | tee -a $log_file
$python_cmd replication/criterias.py --dataset $target_dir --input $target_dir --output criterias/criteria1 --iac-percentage --csv csv/criterias-output/criterias_results.csv 2>&1 | tee -a $log_file || handle_error "First filtering process failed"

echo "Running the second filtering process..." | tee -a $log_file
$python_cmd replication/criterias.py --dataset $target_dir --input criterias/criteria1 --output criterias/criteria2 --fork --csv csv/criterias-output/criterias_results.csv 2>&1 | tee -a $log_file || handle_error "Second filtering process failed"

echo "Running the third filtering process..." | tee -a $log_file
$python_cmd replication/criterias.py --dataset $target_dir --input criterias/criteria2 --output criterias/criteria3 --commits-per-month --csv csv/criterias-output/criterias_results.csv 2>&1 | tee -a $log_file || handle_error "Third filtering process failed"

echo "Running the fourth filtering process..." | tee -a $log_file
$python_cmd replication/criterias.py --dataset $target_dir --input criterias/criteria3 --output criterias/criteria4 --num-contributors --csv csv/criterias-output/criterias_results.csv 2>&1 | tee -a $log_file || handle_error "Fourth filtering process failed"

echo "Creating CSV directories..." | tee -a $log_file
mkdir -p csv/criterias-output/criterias-frequency || handle_error "Failed to create CSV directories"

echo "Generating the CSV with related files..." | tee -a $log_file
$python_cmd replication/1-related-files-generator.py --input $target_dir --output csv/criterias-output/csv1_files_with_neighbors.csv 2>&1 | tee -a $log_file || handle_error "CSV related files generation failed"

echo "Generating the CSV with the commits summary..." | tee -a $log_file
$python_cmd replication/2-commits-count.py --input csv/criterias-output/csv1_files_with_neighbors.csv --output csv/criterias-output/csv2_iac_commits_summary.csv --dataset-dir $target_dir 2>&1 | tee -a $log_file || handle_error "Commits summary CSV generation failed"

echo "Generating the CSV with the time period..." | tee -a $log_file
$python_cmd replication/3-time-period.py --input csv/criterias-output/csv2_iac_commits_summary.csv --output csv/criterias-output/csv3_iac_criterias_output.csv --dataset-dir $target_dir 2>&1 | tee -a $log_file || handle_error "Time period CSV generation failed"

echo "Generating the CSV with frequency..." | tee -a $log_file
$python_cmd replication/4-analyze.py --input csv/criterias-output/csv3_iac_criterias_output.csv --output csv/criterias-output/csv4_iac_output_frequency.csv 2>&1 | tee -a $log_file || handle_error "Frequency CSV generation failed"

echo "Generating criterias frequency csv..." | tee -a $log_file
$python_cmd replication/criteria-frequency.py --input criterias/criteria1,criterias/criteria2,criterias/criteria3,criterias/criteria4,$target_dir --output csv/criterias-output/criterias-frequency 2>&1 | tee -a $log_file || handle_error "Criterias frequency CSV generation failed"

echo "Criterias execution completed. Logs saved to $log_file." | tee -a $log_file
