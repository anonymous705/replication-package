import os
import sys
import subprocess
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

iac_extensions = [".tf", "Pulumi.yaml", "Pulumi.yml", "cdk.json", "cdktf.json", ".edn"]

def is_not_fork(repo_path):
    config_file = os.path.join(repo_path, ".git", "config")
    if not os.path.exists(config_file):
        print(f"[WARNING] {repo_path}: .git/config não encontrado.")
        return None
    with open(config_file, "r") as f:
        is_fork = "fork = true" not in f.read()
        print(f"[INFO] {repo_path}: Fork? {'Não' if is_fork else 'Sim'}")
        return is_fork

def iac_percentage(repo_path):
    total_files = 0
    iac_files = 0
    iac_directories = set()
    for root, _, files in os.walk(repo_path):
        has_iac = any(file_.endswith(ext) for file_ in files for ext in iac_extensions)
        if has_iac:
            iac_directories.add(root)
        total_files += len(files)
    for iac_dir in iac_directories:
        iac_files += sum(len(files) for _, _, files in os.walk(iac_dir))
    percentage = (iac_files / total_files) * 100 if total_files > 0 else 0
    print(f"[INFO] {repo_path}: IaC = {iac_files}/{total_files} arquivos ({percentage:.2f}%)")
    return percentage

def commits_per_month(repo_path):
    result = subprocess.run(
        ["git", "log", "--date=format:%Y-%m", "--pretty=format:%ad"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        text=True
    )
    dates = result.stdout.splitlines()
    unique_months = set(dates)
    cpm = len(dates) / len(unique_months) if unique_months else 0
    print(f"[INFO] {repo_path}: {len(dates)} commits em {len(unique_months)} meses = {cpm:.2f} commits/mês")
    return cpm

def num_contributors(repo_path):
    result = subprocess.run(
        ["git", "log", "--pretty=format:%ae"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        text=True
    )
    all_emails = set(result.stdout.splitlines())
    filtered = {email for email in all_emails if not email.endswith("@github.com")}
    print(f"[INFO] {repo_path}: {len(filtered)} contribuidores (sem bots/github)")
    return len(filtered)

def analyze_repo(repo, dataset_dir, input_dir, output_dir, filters):
    repo_path = os.path.join(dataset_dir, repo)
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print(f"[WARNING] {repo_path} não é um repositório Git válido. Ignorando.")
        return {"repo": repo, "status": "Not a Git repo"}

    input_repos = os.listdir(input_dir) if input_dir else []
    is_input = repo in input_repos

    results = {"repo": repo}
    print(f"[INFO] Analisando repositório: {repo}")

    if filters["--fork"]:
        results["is_not_fork"] = is_not_fork(repo_path)
    if filters["--iac-percentage"]:
        results["iac_percentage"] = iac_percentage(repo_path)
    if filters["--commits-per-month"]:
        results["commits_per_month"] = commits_per_month(repo_path)
    if filters["--num-contributors"]:
        results["num_contributors"] = num_contributors(repo_path)

    passed = True
    if filters["--fork"] and not results.get("is_not_fork", False):
        passed = False
    if filters["--iac-percentage"] and (results.get("iac_percentage") or 0) < 11:
        passed = False
    if filters["--commits-per-month"] and (results.get("commits_per_month") or 0) < 2:
        passed = False
    if filters["--num-contributors"] and (results.get("num_contributors") or 0) < 10:
        passed = False

    results["passed"] = passed
    print(f"[INFO] {repo}: {'PASSOU' if passed else 'NÃO passou'} nos filtros.")

    if passed and is_input:
        target_path = os.path.join(output_dir, repo)
        try:
            if not os.path.exists(target_path):
                os.symlink(os.path.abspath(repo_path), target_path, target_is_directory=True)
                results["link_created"] = True
                print(f"[INFO] Link simbólico criado para {repo}")
            else:
                results["link_created"] = False
                print(f"[INFO] Link simbólico já existia para {repo}")
        except Exception as e:
            results["link_created"] = False
            results["error"] = str(e)
            print(f"[ERROR] Falha ao criar link para {repo}: {e}")
    return results

if __name__=="__main__":
    if "--dataset" not in sys.argv or "--output" not in sys.argv:
        print("Usage: python3 criterias.py --dataset path --input path --output path [--fork] [--iac-percentage] [--commits-per-month] [--num-contributors] [--csv path/to/file.csv]")
        sys.exit(1)

    dataset_dir = os.path.abspath(sys.argv[sys.argv.index("--dataset") + 1])
    output_dir = os.path.abspath(sys.argv[sys.argv.index("--output") + 1])
    input_dir = os.path.abspath(sys.argv[sys.argv.index("--input") + 1]) if "--input" in sys.argv else None
    os.makedirs(output_dir, exist_ok=True)

    # Define caminho do CSV
    if "--csv" in sys.argv:
        csv_path = os.path.abspath(sys.argv[sys.argv.index("--csv") + 1])
    else:
        csv_path = os.path.join(output_dir, "criterias_results.csv")

    filters = {
        "--fork": "--fork" in sys.argv,
        "--iac-percentage": "--iac-percentage" in sys.argv,
        "--commits-per-month": "--commits-per-month" in sys.argv,
        "--num-contributors": "--num-contributors" in sys.argv
    }

    repos = os.listdir(dataset_dir)
    print(f"[INFO] Iniciando análise de {len(repos)} repositórios...")

    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(analyze_repo, repo, dataset_dir, input_dir, output_dir, filters) for repo in repos]
        for i, future in enumerate(futures, 1):
            result = future.result()
            results.append(result)
            print(f"[INFO] {i}/{len(repos)} repositórios processados")

    # Salva CSV
    fieldnames = set()
    new_df = pd.DataFrame(results)

    if os.path.exists(csv_path):
        print(f"[INFO] CSV já existe, atualizando resultados: {csv_path}")
        
        # Carrega CSV existente
        existing_df = pd.read_csv(csv_path)
        # Junta com base na coluna "repo", mantendo dados anteriores e atualizando os novos
        existing_df["repo"] = existing_df["repo"].astype(str)
        new_df["repo"] = new_df["repo"].astype(str)
        merged_df = pd.merge(existing_df, new_df, on="repo", how="outer", suffixes=('', '_new'))

        # Atualiza os campos com os dados novos (colunas *_new), se existirem
        for col in new_df.columns:
            if col != "repo":
                new_col = col + "_new"
                if new_col in merged_df.columns:
                    merged_df[col] = merged_df[new_col].combine_first(merged_df[col])
                    merged_df.drop(columns=[new_col], inplace=True)

        # Salva de volta no CSV
        merged_df.to_csv(csv_path, index=False)
        print(f"[INFO] Resultados atualizados no CSV.")
    else:
        print(f"[INFO] Criando novo CSV em: {csv_path}")
        new_df.to_csv(csv_path, index=False)
        print(f"[INFO] {len(results)} repositórios registrados no novo CSV.")