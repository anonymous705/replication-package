import os
import subprocess
import csv
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

csv.field_size_limit(sys.maxsize)

def is_git_repo(path):
    return os.path.exists(os.path.join(path, ".git"))

def count_commits_for_files(repo_path, file_paths):
    """
    Conta o número de commits relacionados a uma lista de arquivos em um repositório Git.
    """
    unique_commits = set()
    for file_path in file_paths:
        relative_path = os.path.relpath(file_path, repo_path)
        cmd = ["git", "-C", repo_path, "log", "--pretty=%H", "--", relative_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commits = result.stdout.strip().split("\n")
            unique_commits.update(commits)
        except subprocess.CalledProcessError:
            print(f"[ERROR] Falha ao executar git log para arquivo {relative_path} em {repo_path}")
            continue
    return len(unique_commits)

def count_total_commits(repo_path):
    """
    Conta o total de commits do repositório.
    """
    cmd = ["git", "-C", repo_path, "log", "--pretty=%H"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return len(result.stdout.strip().split("\n"))
    except subprocess.CalledProcessError:
        print(f"[ERROR] Falha ao executar git log no repositório {repo_path}")
        return None

def process_repository_row(row, dataset_dir):
    """
    Processa uma linha do CSV (um repositório) e retorna a linha com os campos de commits preenchidos.
    """
    repo_id = row["id"]
    try:
        iac_paths = eval(row["iac_paths"])
        related_files = eval(row["related_files"])
    except Exception as e:
        print(f"[ERROR] Erro ao processar paths do repositório {repo_id}: {e}")
        row["commit_count"] = ""
        row["total_commit_count"] = ""
        return row

    iac_paths = [path for path in iac_paths if path]
    related_files = [path for path in related_files if path]

    if not iac_paths and not related_files:
        print(f"[INFO] Ignorando repositório {repo_id} porque não há arquivos válidos.")
        row["commit_count"] = ""
        row["total_commit_count"] = ""
        return row

    repo_path = os.path.join(dataset_dir, repo_id)

    if not is_git_repo(repo_path):
        print(f"[WARNING] Diretório '{repo_path}' não é um repositório Git.")
        row["commit_count"] = ""
        row["total_commit_count"] = ""
        return row

    file_paths = iac_paths + related_files
    commit_count = count_commits_for_files(repo_path, file_paths)
    total_commits = count_total_commits(repo_path)

    row["commit_count"] = commit_count
    row["total_commit_count"] = total_commits if total_commits is not None else ""
    return row

def process_repositories_and_commits(input_csv, output_csv, dataset_dir):
    """
    Processa o CSV de entrada de forma concorrente, contando commits relacionados aos arquivos IaC
    e salvando o resultado em um CSV de saída.
    """
    with open(input_csv, mode="r") as infile, open(output_csv, mode="w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["commit_count", "total_commit_count"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        rows = list(reader)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(process_repository_row, row, dataset_dir): row for row in rows}

            for future in as_completed(futures):
                result_row = future.result()
                writer.writerow(result_row)

# Entry point
if __name__ == "__main__":
    if "--input" not in sys.argv or "--output" not in sys.argv or "--dataset-dir" not in sys.argv:
        print("Usage: python3 2-commits-count.py --input path --output path --dataset-dir path")
        sys.exit(1)

    input_path = os.path.abspath(sys.argv[sys.argv.index("--input") + 1])
    output = os.path.abspath(sys.argv[sys.argv.index("--output") + 1])
    dataset_dir = os.path.abspath(sys.argv[sys.argv.index("--dataset-dir") + 1])
    process_repositories_and_commits(input_path, output, dataset_dir)
