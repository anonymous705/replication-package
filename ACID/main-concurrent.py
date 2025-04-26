'''
Akond Rahman 
Mar 19, 2019 : Tuesday 
ACID: Main 
'''
import os
import excavator
import constants
import pandas as pd 
import pickle
import time
import datetime
import sys 
import git
import concurrent.futures
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

'''
This script goes to each repo and mines commits and commit messages and then get the defect category 
'''
def getBranchName(path):
    try:
        repo = git.Repo(path)
        default_branch_ref = repo.git.symbolic_ref('refs/remotes/origin/HEAD')
        default_branch = default_branch_ref.replace('refs/remotes/origin/', '')
        return default_branch
    except Exception as e:
        print(f"Error selecting Branch repo {path}: {e}")
        return None

def giveTimeStamp():
  tsObj = time.time()
  strToret = datetime.datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
  return strToret

if __name__=='__main__':

    t1 = time.time()
    print('Started at:', giveTimeStamp()) 
    print('*'*100)

    flag_arg = sys.argv[sys.argv.index("--flag-arg") + 1]
    if flag_arg == '-x': 
       orgName='EXTRA'
       print('ACID will now run on extra testing repos')
       out_fil_nam = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/EXTRA2_TEST_ONLY.PKL'
       out_csv_fil = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/EXTRA2_TEST_ONLY_CATEG_OUTPUT_FINAL.csv'
       out_pkl_fil = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/EXTRA2_TEST_ONLY_CATEG_OUTPUT_FINAL.PKL'
    elif flag_arg == "-replication":
        orgName = 'PIPR-replication'
        print('ACID will now run on PIPr Replication repos')
        out_fil_nam = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/REPLICATION_ONLY.PKL'
        out_csv_fil = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/REPLICATION_ONLY_CATEG_OUTPUT_FINAL.csv'
        out_pkl_fil = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/REPLICATION_ONLY_CATEG_OUTPUT_FINAL.PKL'
    elif flag_arg == "-t":
        orgName='TEST'
        print('ACID will now run on default testing repos')
        out_fil_nam = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/TEST2_ONLY.PKL'
        out_csv_fil = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/TEST2_ONLY_CATEG_OUTPUT_FINAL.csv'
        out_pkl_fil = '/home/aluno/ACID-dataset/ARTIFACT/OUTPUT/TEST2_ONLY_CATEG_OUTPUT_FINAL.PKL' 
    else:
        orgName = flag_arg
        print(f'ACID will now run on {flag_arg} repos')
        output_location = os.path.abspath(sys.argv[sys.argv.index("--output") + 1])
        out_fil_nam     = output_location + f'/{flag_arg}_ONLY.PKL'
        out_csv_fil     = output_location + f'/{flag_arg}_CATEG_OUTPUT_FINAL.csv'
        out_pkl_fil     = output_location + f'/{flag_arg}_ONLY_CATEG_OUTPUT_FINAL.PKL'
    def process_project(orgName, proj_, pathRepo, dic, categ, csv_replication, csv_default):
     try:
        if proj_ == constants.REPO_FILE_LIST: return
        path_proj = pathRepo + proj_
        branchName = getBranchName(path_proj)
        
        if branchName is None:
            raise Exception(f"Branch name not found for project {proj_}")

        per_proj_commit_dict, per_proj_full_defect_list = excavator.runMiner(orgName, proj_, branchName, csv_replication, csv_default)
        
        categ += per_proj_full_defect_list
        dic[proj_] = (per_proj_commit_dict, per_proj_full_defect_list)

        print(f'Finished analyzing: {proj_}')
        print("="*50)
     except Exception as e:
        print(f"Error processing project {proj_}: {e}")

    def run_in_parallel(orgName, elgibleRepos, pathRepo, dic, categ, csv_replication, csv_default):
     with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_project, orgName, proj_, pathRepo, dic, categ, csv_replication, csv_default) for proj_ in elgibleRepos]
        
        # Wait for all tasks to complete and handle exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Retrieve the result of the task (or raise any exceptions)
            except Exception as e:
                print(f"Task raised an exception: {e}")
    
    if orgName == 'EXTRA' or orgName == "TEST" or orgName == "PIPR-replication":
        csv_replication = None
        csv_default     = None
    else:
        csv_replication = os.path.abspath(sys.argv[sys.argv.index("--csv-replication") + 1])
        csv_default     = os.path.abspath(sys.argv[sys.argv.index("--csv-default") + 1])
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pathRepo = script_dir + "/" + constants.DATASET_DIR + "/" + orgName + "/"
    fileName = pathRepo + "/" + constants.REPO_FILE_LIST
    elgibleRepos = excavator.getEligibleProjects(fileName)
    dic   = {}
    categ = []
    run_in_parallel(orgName, elgibleRepos, pathRepo, dic, categ, csv_replication, csv_default)
    
    all_proj_df = pd.DataFrame(categ) 
    all_proj_df.to_csv(out_csv_fil, header=['HASH','CATEG','REPO','TIME'], index=False) 

    with open(out_pkl_fil, 'wb') as fp_:
        pickle.dump(dic, fp_)  
    print('*'*100)
    print('Ended at:', giveTimeStamp())
    print('*'*100)
    t2 = time.time()
    time_diff = round( (t2 - t1 ) / 60, 5) 
    print("Duration: {} minutes".format(time_diff))
    print('*'*100)        
