#!/bin/bash

# Initial configurations
default_dir="dataset"
log_file="clone_logs.csv"
repos_file="repos_list.txt" # File with the list of repositories
threads=10 # Number of threads
start_line=2 # Default starting line

function usage() {
  echo "Usage: $0 [-d directory] [-f repos_file] [-s start_line] [-t threads] [-c credential]"
  echo "Options:"
  echo "  -d  Destination directory for cloning repositories (default: dataset)"
  echo "  -f  File containing the list of repositories (one per line) (default: repos_list.txt)"
  echo "  -s  Starting line to continue cloning (default: 2)"
  echo "  -t  Number of simultaneous clones (default: 10)"
  echo "  -c  Credential type: ssh or token"
  exit 1
}

# Process arguments
while getopts "d:f:s:t:c:" opt; do
  case "$opt" in
    d) target_dir="$OPTARG" ;;
    f) repos_file="$OPTARG" ;;
    s) start_line="$OPTARG" ;;
    t) threads="$OPTARG" ;;
    c) credential_type="$OPTARG" ;;
    *) usage ;;
  esac
done

[[ -z "$target_dir" ]] && target_dir="$default_dir"
[[ -z "$credential_type" ]] && credential_type="ssh"

# Initial validations
if [[ ! -f "$repos_file" ]]; then
  echo "Error: Repositories file ($repos_file) not found."
  exit 1
fi

if [[ "$credential_type" != "ssh" && "$credential_type" != "token" ]]; then
  echo "Error: Invalid credential type. Use 'ssh' or 'token'."
  exit 1
fi

# The following command can prevent parallelism errors
# It increases the limit of open files
ulimit -n 4096

mkdir -p "$target_dir"
echo "Destination directory created at ($target_dir)"

if [[ ! -f "$log_file" ]]; then
  echo "Repository,Status,Message" > "$log_file"
fi
echo "Log file created at ($log_file)"

clone_repo() {
  local repo_url="$1"
  local repo_name=$(basename -s .git "$repo_url")

  if [[ "$credential_type" == "token" && "$repo_url" == https://* ]]; then
    repo_url=$(echo "$repo_url" | sed "s|https://|https://$github_token@|")
  fi

  echo "Cloning $repo_name..."

  if git clone "$repo_url" "$target_dir/$repo_name" &>/dev/null; then
    echo "$repo_url,Success," >> "$log_file"
    echo "[OK] $repo_name cloned successfully."
  else
    echo "$repo_url,Error,Failed to clone" >> "$log_file"
    echo "[ERROR] Failed to clone $repo_name."
  fi
}

export -f clone_repo
export credential_type
github_token=""

if [[ "$credential_type" == "token" ]]; then
  echo "Enter the GitHub token: "
  read -s github_token
  export github_token
fi
export target_dir
export log_file

# Process repositories in parallel
repos_to_clone=$(tail -n +$start_line "$repos_file")
echo "$repos_to_clone" | xargs -P $threads -n 1 -I {} bash -c 'clone_repo "$1"' _ {}

mkdir -p csv
mv "$log_file" "csv/$log_file"

find "$target_dir" -type d -exec chmod +x {} \;

echo "Process completed. Logs saved in csv/$log_file."
