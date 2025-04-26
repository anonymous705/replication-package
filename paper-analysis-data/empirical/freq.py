'''
Akond Rahman 
June 01 2019 
Saturday 
'''
import re
import git
import pandas as pd 
import numpy as np 
import os 
import hglib 
from git import Repo
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

def extract_repo_root(path):
    match = re.match(r"(.*?/REPLICATION/[^/]+)", path)
    return match.group(1) if match else None

def days_between(d1_, d2_): ## pass in date time objects, if string see commented code 
    # d1_ = datetime.strptime(d1_, "%Y-%m-%d")
    # d2_ = datetime.strptime(d2_, "%Y-%m-%d")
    return abs((d2_ - d1_).days)

def getBranchName(path):
    try:
        repo = git.Repo(path)
        default_branch_ref = repo.git.symbolic_ref('refs/remotes/origin/HEAD')
        default_branch = default_branch_ref.replace('refs/remotes/origin/', '')
        return default_branch
    except Exception as e:
        print(f"Error selecting Branch repo {path}: {e}")
        return None

def changeCategIfNeeded(categ_param):
    categ_mod = ''
    mod_dict  = {
                'BUILD_DEFECT':'SERVICE_DEFECT', 
                'DB_DEFECT':'SERVICE_DEFECT', 
                'INSTALL_DEFECT':'SERVICE_DEFECT', 
                'LOG_DEFECT':'SERVICE_DEFECT', 
                'NET_DEFECT':'SERVICE_DEFECT', 
                'RACE_DEFECT':'SERVICE_DEFECT'
                }
    if categ_param in mod_dict:
        categ_mod = mod_dict[categ_param]
    else:
        categ_mod = categ_param
    return categ_mod

def getFullCategFreq(file_name):
    categ_dict   = {}
    full_df      = pd.read_csv(file_name) 
    full_hash_ls =  np.unique( full_df['HASH'].tolist() )
    tot_hash_cnt = len(full_hash_ls)
    print('DATASET:', file_name)
    print('TOTAL_COMMIT_COUNT:', tot_hash_cnt)
    print('=' * 100)

    for indi_hash in full_hash_ls:
        indi_hash_df    = full_df[full_df['HASH']==indi_hash] 
        indi_hash_categ = np.unique(indi_hash_df['CATEG'].tolist())

        for categ_ in indi_hash_categ:
            categ_ = changeCategIfNeeded(categ_)
            if categ_ not in categ_dict:
                categ_dict[categ_] = [indi_hash] 
            else:
                categ_dict[categ_] = [indi_hash] + categ_dict[categ_] 
    for categ, hash_list in categ_dict.items():
        categ_count        = len(np.unique(hash_list))
        prop_defect_commit = (float(categ_count)/float(tot_hash_cnt))*100 
    
        print('CATEG:{}, RAW_COUNT:{}, PROP_DEFECT_COMMIT:{}'.format(categ, categ_count, prop_defect_commit))
        print('*' * 50)


def getDay(single_time):
    day_ = single_time.split('T')[0] 
    return day_  

def getOnlyDefectCategFreq(file_name):
    categ_dict   = {}
    full_df      = pd.read_csv(file_name) 

    full_hash_ls =  np.unique( full_df['HASH'].tolist() )
    tot_hash_cnt = len(full_hash_ls)

    only_defect_df      = full_df[full_df['CATEG']!='NO_DEFECT']
    only_defect_hash_ls = np.unique( only_defect_df['HASH'].tolist() )
    only_defect_count   = len(only_defect_hash_ls) 
    print('DATASET:', file_name)
    print('ONLY_DEFECT_COMMIT_COUNT:', only_defect_count)
    print('=' * 100)

    for indi_hash in full_hash_ls:
        indi_hash_df    = only_defect_df[only_defect_df['HASH']==indi_hash] 
        indi_hash_categ = np.unique(indi_hash_df['CATEG'].tolist())

        for categ_ in indi_hash_categ:
            categ_ = changeCategIfNeeded(categ_)
            if categ_ not in categ_dict:
                categ_dict[categ_] = [indi_hash] 
            else:
                categ_dict[categ_] = [indi_hash] + categ_dict[categ_] 
    for categ, hash_list in categ_dict.items():
        categ_count        = len(np.unique(hash_list))
        prop_defect_commit = (float(categ_count)/float(only_defect_count))*100 
    
        print('CATEG:{}, RAW_COUNT:{}, ONLY_DEFECT_COUNT:{}, ONLY_DEFECT_PROP:{}'.format(categ, categ_count, only_defect_count, prop_defect_commit))
        print('*' * 50)


def getAtLeastOne(file_param):
    print('=' * 100)
    full_df = pd.read_csv(file_param)
    full_hash_ls = np.unique(full_df['HASH'].tolist())
    tot_hash_cnt = len(full_hash_ls)
    print('DATASET:', file_param)
    print('TOTAL_COMMIT_COUNT:', tot_hash_cnt)
    only_defect_df = full_df[full_df['CATEG'] != 'NO_DEFECT']
    only_defect_hash = np.unique(only_defect_df['HASH'].tolist())
    only_defect_cnt = len(only_defect_hash)
    atleast_one_hash = (float(only_defect_cnt) / float(tot_hash_cnt)) * 100
    print('AT_LEAST_ONE_DEFECT_RELATED_COMMIT:{}, PERC:{}'.format(only_defect_cnt, atleast_one_hash))
    print('=' * 100)
  

iac_extensions_and_support = [
    "Pulumi.yaml", "Pulumi.yml", "cdk.json", "cdktf.json",
    ".py", ".go", ".js", ".ts", ".java", ".tf",
    ".cs", ".fs", ".vb", ".cpp", ".kt", ".php", ".rb", ".swift", ".abap", ".edn"
]

only_iac_extensions = [
    "Pulumi.yaml", "Pulumi.yml", "cdk.json", "cdktf.json", ".tf", ".edn", ".pp"
]

def getRepoDetails(_dir):
    if not os.path.isdir(_dir):
        print(f"[ERRO] Diretório não encontrado: {_dir}")
        return [], []

    all_files, iac_files = [] , []
    for root_, dirs, files_ in os.walk(_dir):
        for file_ in files_:
            full_p_file = os.path.join(root_, file_)
            all_files.append(full_p_file)

    for root_, dirs, files_ in os.walk(_dir):
        for file_ in files_:
            full_p_file = os.path.join(root_, file_)
            if any(full_p_file.endswith(ext) for ext in only_iac_extensions):
                iac_files.append(full_p_file)

    return all_files, iac_files

def getHgCommitCount(repo_name):
    repo_complete = hglib.open(repo_name)
    all_commits = repo_complete.log()

    return all_commits 

def getGitCommitCount(repo_name):
    base_path = extract_repo_root(repo_name)
    branchName = getBranchName(base_path) 
    repo_  = Repo(base_path)
    all_commits = list(repo_.iter_commits(branchName))
    return all_commits     

def getSummary(out_fil):
    all_files, pp_files, all_commits = [], [], []
    df_ = pd.read_csv(out_fil) 
    pupp_hashes = np.unique( df_['HASH'].tolist() ) 
    repos = np.unique( df_['REPO'].tolist() ) 
    df_['DAY'] = df_['TIME'].apply(getDay) 
    all_day_list   = np.unique( df_['DAY'].tolist() )
    all_day_list   = [datetime(int(x_.split('-')[0]), int(x_.split('-')[1]), int(x_.split('-')[2]), 12, 30) for x_ in all_day_list]
    min_day        = min(all_day_list) 
    max_day        = max(all_day_list) 
    ds_life_days   = days_between(min_day, max_day)
    ds_life_months = round(float(ds_life_days)/float(30), 5)


    for repo_ in repos:
        repo_all_files, repo_pp_files = getRepoDetails(repo_) 
        all_files = all_files + repo_all_files 
        pp_files  = pp_files + repo_pp_files 
        if 'mozilla-releng-downloads' in repo_: 
            all_commits = all_commits + getHgCommitCount(repo_)
        else:
            all_commits = all_commits + getGitCommitCount(repo_)
    pp_files_loc = [sum(1 for line in open(x_ , 'rU')) for x_ in pp_files if os.path.exists(x_) ]
    ds_comm_mon  = round(float(len(all_commits))/float(ds_life_months), 5)

    print('=' * 100)
    print('Dataset name:', out_fil.split('/')[-1])
    print('Total repo count:', len(repos))
    print('Total duration: First:{}, last:{} duration in months:{}'.format(min_day, max_day, ds_life_months))
    print('Total commits:', len(all_commits))
    print('Dataset commit per month:', ds_comm_mon)
    print('Total puppet-related commits:', len(pupp_hashes))
    print('Total files:', len(all_files))
    print('Total Puppet scripts:', len(pp_files))
    print('Total Puppet LOC:', sum(pp_files_loc))
    print('=' * 100)
    

def process_repo(repo_):
    repo_all_files, repo_pp_files = getRepoDetails(repo_)
    if 'mozilla-releng-downloads' in repo_:
        all_commits = getHgCommitCount(repo_)
    else:
        all_commits = getGitCommitCount(repo_)
    
    pp_files_loc = [
        sum(1 for line in open(x_, 'r', encoding='utf-8', errors='ignore', newline='')) 
        for x_ in repo_pp_files 
        if os.path.exists(x_)
    ]
    
    return {
        "repo": repo_,
        "all_files": repo_all_files,
        "pp_files": repo_pp_files,
        "all_commits": all_commits,
        "pp_files_loc": pp_files_loc
    }


def getSummaryParallel(out_fil):
    df_ = pd.read_csv(out_fil)
    df_['DAY'] = df_['TIME'].apply(getDay)
    all_day_list = [datetime.strptime(x, "%Y-%m-%d") for x in df_['DAY'].unique()]
    min_day, max_day = min(all_day_list), max(all_day_list)
    ds_life_months = days_between(min_day, max_day) / 30.0

    df_['REPO_ROOT'] = df_['REPO'].apply(extract_repo_root)
    repos = df_['REPO_ROOT'].dropna().unique()
    
    all_files, pp_files, all_commits, pp_files_loc = [], [], [], []

    with ThreadPoolExecutor(max_workers=(multiprocessing.cpu_count() - 1)) as executor:
        futures = [executor.submit(process_repo, repo_) for repo_ in repos]
        for future in as_completed(futures):
            result = future.result()
            all_files += result['all_files']
            pp_files += result['pp_files']
            all_commits += result['all_commits']
            pp_files_loc += result['pp_files_loc']

    ds_comm_mon = round(len(all_commits) / ds_life_months, 5)

    print('=' * 100)
    print('Dataset name:', out_fil.split('/')[-1])
    print('Total repo count:', len(repos))
    print(f'Total duration: First:{min_day}, Last:{max_day}, Duration in months:{ds_life_months:.2f}')
    print('Total commits:', len(all_commits))
    print('Dataset commit per month:', ds_comm_mon)
    print('Total Puppet-related commits:', len(df_['HASH'].unique()))
    print('Total files:', len(all_files))
    print('Total Puppet scripts:', len(pp_files))
    print('Total Puppet LOC:', sum(pp_files_loc))
    print('=' * 100)


if __name__=='__main__':
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_OUTPUT_FINAL.csv'
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_OUTPUT_FINAL.csv'    
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_OUTPUT_FINAL.csv'
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_OUTPUT_FINAL.csv'
    acid_output_file = '/home/aluno/Documentos/go8-replication-tool/csv/acid-output/REPLICATION_CATEG_OUTPUT_FINAL.csv'


    '''
    Config sub category 
    '''
    # acid_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_SUBCONFIG_FINAL.csv'
    # acid_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_SUBCONFIG_FINAL.csv'
    # acid_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_SUBCONFIG_FINAL.csv'
    # acid_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_SUBCONFIG_FINAL.csv'
    # acid_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/ALL_CATEG_SUBCONFIG_FINAL.csv'

    getFullCategFreq(acid_output_file)
    getAtLeastOne(acid_output_file)

    '''
    dataset summary: one time use 
    ''' 
    getSummaryParallel(acid_output_file) 