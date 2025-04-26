# Replication Package for "A Defect Taxonomy for Infrastructure as Code Scripts: A Replication Study"

As Infrastructure as Code (IaC) becomes standard practice, ensuring the reliability of IaC scripts is essential. Defect taxonomies are valuable tools for this, offering a common language for issues and enabling systematic tracking. This repository provides a full replication package for the study "A Defect Taxonomy for Infrastructure as Code Scripts: A Replication Study", including results, the source code, and step-by-step instructions for reproducing all experiments. 

**Contents:**
* Dataset & Reproducibility
* Directory Structure (Source Code)
* Replication Tool

## Dataset & Reproducibility

This repository contains the full source code and detailed instructions needed to reproduce the results presented in the paper "A Defect Taxonomy for Infrastructure as Code Scripts: A Replication Study". The PIPr dataset used in the experiments and a permanent archive of code is hosted on Zenodo: https://doi.org/10.5281/zenodo.15276124.

## Directory Structure (Source Code)

The structure of this repository is defined below, including directories, documents, and scripts.

### ACID
Original study tool being replicated, available at: https://hub.docker.com/r/akondrahman/acid-puppet
* `classifier.py`: classifies commit messages into defect categories using NLP and rule-based analysis.
* `constants.py`: stores configuration strings, keywords, and constants for defect categorization.
* `diff_parser.py`: analyzes Git diff content to detect code changes related to specific defect types.
* `excavator.py`: extracts and processes IaC-related commits from Git repositories for defect analysis.
* `main-concurrent.py`: concurrent version of the main script.
* `main.py`: main script to mine and categorize defects in IaC commits.

### criterias
This directory is generated after the tool is executed.
* `criteria1`: repositories that passed the 1st criterion: not being a fork.
* `criteria2`: repositories that passed the 1st and 2nd criteria: at least 11% of files are IaC and/or PL-IaC scripts.
* `criteria3`: repositories that passed the 1st, 2nd, and 3rd criteria: monthly commit frequency is ≥ 2.
* `criteria4`: repositories that passed all four criteria: number of contributors is ≥ 10.

### csv
This directory is generated after the tool is executed.
* `acid-output/REPLICATION_CATEG_OUTPUT_FINAL.csv`: ACID output.
* `acid-output/REPLICATION_ONLY_CATEG_OUTPUT_FINAL.PKL`: serialized ACID output.
* `criterias-output/criterias-frequency/criteria1_output.csv`: repository ID and technology for those that passed the 1st criterion.
* `criterias-output/criterias-frequency/criteria2_output.csv`: repository ID and technology for those that passed the 1st and 2nd criteria.
* `criterias-output/criterias-frequency/criteria3_output.csv`: repository ID and technology for those that passed the 1st, 2nd, and 3rd criteria.
* `criterias-output/criterias-frequency/criteria4_output.csv`: repository ID and technology for those that passed all four criteria.
* `criterias-output/criterias-frequency/dataset_output.csv`: repository ID and technology for all analyzed repositories, regardless of criteria.
* `criterias-output/criterias_results.csv`: individual data for each repository and its corresponding criteria.
* `criterias-output/csv1_files_with_neighbors.csv`: paths of IaC files and their neighboring related files.
* `criterias-output/csv2_iac_commits_summary.csv`: commit counts for IaC paths and the entire repository.
* `criterias-output/csv3_iac_criterias_output.csv`: data on the oldest and most recent commits and their deltas.
* `criterias-output/csv4_iac_output_frequency.csv`: summary of repository attributes.
* `clone_logs.csv`: logs related to repository cloning (success or failure).

### dataset
Contains all repositories selected for cloning.

### paper-analysis-data
Intermediate results used in study, including 42 files and 10 subdirectories.

* `empirical`: scripts, metrics and data related to defect categories.
* `oracle`: comparison between the categorization performed by the oracle and by ACID.
* `PIPr-results`: include all csvs related to ACID execution in PIPr.
* `plots`: defect/year metric across datasets.
* `sanity-validation`: sanity check for repositories, including metrics.

### replication
* `1-related-files-generator.py`: identifies IaC files and related neighboring files within repositories.
* `2-commits-count.py`: counts the number of commits associated with identified IaC and related files.
* `3-time-period.py`: determines the time period of commits related to IaC files in repositories.
* `4-analyze.py`: aggregates and analyzes data from processed repositories to generate summary statistics.
* `criteria-frequency.py`: classifies repositories based on detected IaC technology within specified directories.
* `criterias.py`: applies predefined criteria to filter and select relevant IaC repositories.

Other relevant files:

* `README.md`
* `apply-criterias.sh`: shell script to execute the repository filtering process based on defined criteria.
* `clone-repos.sh`: shell script to clone a list of Git repositories in parallel.
* `repos_list.txt`: contains a list of repository URLs to be cloned.
* `requirements.txt`: dependencies required to run the project.
* `run-acid.sh`: shell script to execute the main defect analysis pipeline (ACID).


## Replication Tool

### Setup

- The `spacy` library needs to be used in **version 3.8.3**, which currently (April 2025) is only **compatible with Python 3.10 or 3.11**.
- Utilize either the Linux or macOS operating systems to execute the tool.

### If you are using virtual environment (venv)

**1.** Check the Python version in the environment:
   ```bash
   $ ./<your-venv-name>/bin/python --version
   ```

**2.** If it is not Python 3.10 or 3.11, install using `pyenv`:
   ```bash
   # Install pyenv
   curl https://pyenv.run | bash

   # Add to your shell (~/.bashrc, ~/.zshrc, ...)
   export PATH="$HOME/.pyenv/bin:$PATH"
   eval "$(pyenv init --path)"
   eval "$(pyenv init -)"
   ```
**3.** Install the compatible Python version and recreate the venv:
   ```bash
   pyenv install 3.11.7
   pyenv local 3.11.7

   python -m venv <your-venv-name>
   source <your-venv-name>/bin/activate
   pip install -r requirements.txt
   ```

### If you are NOT using virtual environment (venv)

**1.** Check the Python version:
   ```bash
   python --version
   ```

**2.** If it is not Python 3.10 or 3.11, use `pyenv` to install the compatible Python version:
   ```bash
   pyenv install 3.11.7
   pyenv global 3.11.7
   ```

**3.** Install the dependencies:
```bash
pip install -r requirements.txt
```

> **Note:** If you encounter any issues installing the packages, the following command may be helpful:

```bash
pip install -r requirements.txt --break-system-packages
```

**4.** After installing all the packages, run the following command:
```bash
python3 -m spacy download en_core_web_sm
```

### Script Execution Guide

**1.** Populate the `repos_list.txt` file with the links of all repositories intended for cloning.

**2.** Subsequently, the cloning script can be executed:

```bash
./clone-repos.sh
```

```bash
"Usage: ./clone-repos.sh [-d directory] [-f repos_file] [-s start_line] [-t threads] [-c credential]

Options:
    -d  Destination directory for cloning the repositories (default: dataset)
    -f  File containing the list of repositories (one per line) (default: repos_list.txt)
    -s  Starting line to resume the cloning process (default: 2)
    -t  Number of concurrent clones (default: 10)
    -c  Credential type: ssh or token"
```

Upon completion of the execution, the repositories will be cloned to the specified destination. Additionally, a CSV file will be generated within the `csv` directory, indicating the success or failure status of each repository's cloning process.

> **Note:** Depending on the number of threads chosen, you may encounter a "Too Many Open Files" error. To resolve this, you can redefine the limit for concurrently open files using the following command:

```bash
# The default is 1024; a higher number such as 4096 can be selected.
ulimit -n 4096
```

**3.** Apply selection criteria and generate the necessary CSV files for analysis with the following command:

```bash
./apply-criterias.sh
```

```bash
"Usage: ./apply-criterias.sh [-d directory]
Options:
    -d  Destination directory where the repositories were cloned (default: dataset)"
```

**4.** Execute the defect categorization tool, which is available in two versions: concurrent and serial.

```bash
./run-acid.sh
```

```bash
"Usage: ./run-acid [-c]
Options:
    -c  This option will utilize 'main-concurrent.py' instead of 'main.py'."
```

### Toy Example

> **Note**: All scripts generate logs, and in the event of a failure, the reason can be investigated.

**1.** Add a repository to clone list:
```bash
echo "https://github.com/mitodl/ol-infrastructure" >> repos_list.txt
```

**2.** Clone repository:
```bash
./clone-repos.sh
```

> **Note**: As this repository is public, authentication is not required. For private repositories, it is necessary to provide the type of authentication desired:
```bash
# SSH
./clone-repos.sh -c ssh
# Token
./clone-repos.sh -c token
```

**3.** Apply repository selection criterias:
```bash
./apply-criterias.sh
```

**4.** Execute the tool:
```bash
# Serial version
./run-acid 
# Concurrent version (RECOMMENDED)
./run-acid -c
```

**5.** Finally, all the results will be located within the `csv` directory. These include the execution results, defect categorization of the repositories and a summary of the repositories characteristics (e.g., the number of Pulumi, AWS CDK, Terraform, or EDN languages).
