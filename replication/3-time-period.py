import os
import subprocess
import csv
from datetime import datetime
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

csv.field_size_limit(sys.maxsize)

def get_commit_time_period(repo_path, file_paths):
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print(f"[WARNING] Diretório '{repo_path}' não é um repositório Git. Ignorando.")
        return None, None

    commit_dates = []
    for file_path in file_paths:
        relative_path = os.path.relpath(file_path, repo_path)
        cmd = ["git", "-C", repo_path, "log", "--pretty=%ci", "--", relative_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            dates = result.stdout.strip().split("\n")
            commit_dates.extend(dates)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] git log falhou para '{relative_path}' em '{repo_path}': {e}")
            return None, None

    valid_dates = []
    for date in commit_dates:
        try:
            valid_dates.append(datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z"))
        except ValueError as e:
            print(f"[WARNING] Data inválida '{date}' em {repo_path}: {e}")
            continue

    if not valid_dates:
        print(f"[WARNING] Nenhuma data válida em '{repo_path}'.")
        return None, None

    return min(valid_dates), max(valid_dates)


def process_row(row, dataset_dir):
    repo_id = row["id"]
    iac_paths = eval(row["iac_paths"])
    repo_path = os.path.join(dataset_dir, repo_id)

    try:
        oldest_commit, newest_commit = get_commit_time_period(repo_path, iac_paths)

        if oldest_commit and newest_commit:
            commit_time_period = (newest_commit - oldest_commit).days
            print(f"[INFO] {repo_id}: Período de commits = {commit_time_period} dias")
        else:
            commit_time_period = None
            print(f"[INFO] {repo_id}: Sem dados de commit válidos.")

        row["oldest_commit"] = oldest_commit.strftime("%Y-%m-%d %H:%M:%S %z") if oldest_commit else "N/A"
        row["newest_commit"] = newest_commit.strftime("%Y-%m-%d %H:%M:%S %z") if newest_commit else "N/A"
        row["commit_time_period"] = commit_time_period

    except Exception as e:
        print(f"[ERROR] Erro ao processar '{repo_id}': {e}")
        row["oldest_commit"] = "N/A"
        row["newest_commit"] = "N/A"
        row["commit_time_period"] = "N/A"

    return row


def process_time_period(input_csv, output_csv, dataset_dir):
    with open(input_csv, mode="r") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["oldest_commit", "newest_commit", "commit_time_period"]
        rows = list(reader)

    print(f"[INFO] Iniciando processamento de {len(rows)} repositórios...")

    results = []
    with ThreadPoolExecutor() as executor:
        future_to_row = {executor.submit(process_row, row, dataset_dir): row for row in rows}
        for i, future in enumerate(as_completed(future_to_row), 1):
            result = future.result()
            results.append(result)
            print(f"[INFO] Processados {i}/{len(rows)} repositórios")

    with open(output_csv, mode="w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"[DONE] Todos os repositórios foram processados com sucesso.")
    print(f"[DONE] Resultados salvos em: {output_csv}")


if __name__ == "__main__":
    if not "--input" in sys.argv or not "--output" in sys.argv or not "--dataset-dir" in sys.argv:
        print("Usage: python3 3-time-period.py --input path --output path --dataset-dir path")
        sys.exit(1)
    
    input_path = os.path.abspath(sys.argv[sys.argv.index("--input") + 1])
    output = os.path.abspath(sys.argv[sys.argv.index("--output") + 1])
    dataset_dir = os.path.abspath(sys.argv[sys.argv.index("--dataset-dir") + 1])
    process_time_period(input_path, output, dataset_dir)
