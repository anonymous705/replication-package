'''
Akond Rahman 
June 27, 2019 
Get Metrics Per Category 
'''
import pandas as pd 
import numpy as np 

metric_list = ['MOD_FILES', 'DIRS',	'TOT_SLOC',	'SPREAD', 'DEV_CNT_MOD_FILES', 'DEV_EXP', 'DEV_REXP']

def changeCategIfNeeded(categ_param):
    categ_mod = ''
    mod_dict  = {
                'BUILD_DEFECT':'SERVICE_DEFECT', 
                'DB_DEFECT':'SERVICE_DEFECT', 
                'INSTALL_DEFECT':'SERVICE_DEFECT', 
                'LOG_DEFECT':'SERVICE_DEFECT', 
                'NET_DEFECT':'SERVICE_DEFECT', 
                'RACE_DEFECT':'SERVICE_DEFECT',
                'CONFIG_DATA_DEFECT': 'CONFIG_DEFECT',
                'CD_NETWORK_DEFECT': 'CONFIG_DEFECT',
                'CD_STORAGE_DEFECT':'CONFIG_DEFECT',
                'CD_CACHE_DEFECT':'CONFIG_DEFECT',
                'CD_CREDENTIAL_DEFECT':'CONFIG_DEFECT',
                'CD_FILE_SYSTEM_DEFECT':'CONFIG_DEFECT',
                'SERVICE_RESOURCE_DEFECT':'SERVICE_DEFECT',
                'SERVICE_PANIC_DEFECT': 'SERVICE_DEFECT',
                'BUGGY_COMMIT': 'NO_DEFECT'
                }
    if categ_param in mod_dict:
        categ_mod = mod_dict[categ_param]
    else:
        categ_mod = categ_param
    return categ_mod

def getMetricDist(categ_f, metric_f): 
    categ_df  = pd.read_csv(categ_f) 
    metric_df = pd.read_csv(metric_f) 
    result_df = pd.merge(categ_df, metric_df, on=['HASH'])
    result_df['CHANGED_CATEG'] = result_df['CATEG'].apply(changeCategIfNeeded) 
    categ_list = np.unique(result_df['CHANGED_CATEG'].tolist())
    for categ_ in categ_list:
        per_categ_df = result_df[result_df['CHANGED_CATEG']==categ_]
        print('CATEGORY:',  categ_)
        for metr_ in metric_list:
            metr_vals = per_categ_df[metr_].tolist() 
            if len(metr_vals) > 0 :
                print('METRIC:{}, MIN:{}, MEDIAN:{}, AVG:{}, MAX:{}'.format(metr_,  min(metr_vals), np.median(metr_vals), np.mean(metr_vals), max(metr_vals) ))
                print('-'*10)
            else: 
                print('METRIC:{}, MIN:{}, MEDIAN:{}, AVG:{}, MAX:{}'.format(metr_, 0, 0, 0, 0 ))
                print('-'*10)
        print('*'*50)

def getFileDist(categ_f, hash_mapping_f): 
    if isinstance(categ_f, str):
        categ_df = pd.read_csv(categ_f)
    else:
        categ_df = categ_f

    if isinstance(hash_mapping_f, str):
        map_df = pd.read_csv(hash_mapping_f)
    else:
        map_df = hash_mapping_f

    full_df = pd.merge(categ_df, map_df, on=['HASH'])
    all_files = list(np.unique(full_df['FILE'].tolist()))
    
    print('Dataset name:', categ_f.split('/')[-1] if isinstance(categ_f, str) else 'Provided DataFrame') 
    print('='*50) 
    
    atleast_one_files = []  # Lista para armazenar os arquivos que têm pelo menos um defeito
    full_df['CHANGED_CATEG'] = full_df['CATEG'].apply(changeCategIfNeeded)
    categ_list = np.unique(full_df['CHANGED_CATEG'].tolist())

    for categ_ in categ_list:
        per_categ_file_list = []
        for file_ in all_files:
            file_df = full_df[full_df['FILE'] == file_].copy()
            file_df['CHANGED_CATEG'] = file_df['CATEG'].apply(changeCategIfNeeded)
            categ_file_df = file_df[file_df['CHANGED_CATEG'] == categ_]
            files_categ = list(np.unique(categ_file_df['FILE'].tolist()))
            per_categ_file_list += files_categ

            if categ_ != 'NO_DEFECT': 
                atleast_one_files += files_categ

        per_categ_file_list = list(np.unique(per_categ_file_list))  # Remover duplicatas
        per_categ_file_prop = round(len(per_categ_file_list) / float(len(all_files)), 5) * 100

        if categ_ != 'NO_DEFECT': 
            print(f'CATEGORY: {categ_}')
            print(f' - SCRIPT COUNT: {len(per_categ_file_list)}')
            print(f' - SCRIPT PROP(%): {per_categ_file_prop}')
            print('*' * 25)

    atleast_one_files = list(np.unique(atleast_one_files))  # Remover duplicatas
    atleast_one = round(len(atleast_one_files) / float(len(all_files)), 5) * 100
    print(f'IaC scripts with at least one defect category: {len(atleast_one_files)}')
    print(f'IaC scripts with at least one defect category (%): {atleast_one}')
    print('=' * 50)




def analyzeCommitsForCoOccurence(file_name):
    dict_output          = {2:[], 3: [], 4: [], 5: [], 6: [], 7:[], 8:[]}
    categ_df_full        = pd.read_csv(file_name) 
    df_only_defect_categ = categ_df_full[categ_df_full['CATEG']!='NO_DEFECT']
    df_only_defect_categ['CHANGED_CATEG'] = df_only_defect_categ['CATEG'].apply(changeCategIfNeeded) 
    commits              = np.unique( df_only_defect_categ['HASH'].tolist() )
    for commit_hash in commits:
        commit_df        = df_only_defect_categ[df_only_defect_categ['HASH']==commit_hash]
        commit_categs    = list ( np.unique( commit_df['CHANGED_CATEG'].tolist() ) )
        commit_categ_cnt = len(commit_categs)  
        if commit_categ_cnt > 1:
            dict_output[commit_categ_cnt] = dict_output[commit_categ_cnt] + [commit_hash]  
    return dict_output     

def getCommitCoOccurence(categ_file): 
    print(categ_file)
    categ_df_full        = pd.read_csv(categ_file) 
    categ_commits        = list( np.unique( categ_df_full['HASH'].tolist() ) )
    dict_output = analyzeCommitsForCoOccurence(categ_file)
    print('*'*50)
    for k_, v_ in dict_output.items():
        def_pop = round( (float(len(v_))/float(len(categ_commits)) ) * 100, 5)
        print('{} categories of defects observed for {}% commits (defect proportion)'.format(k_, def_pop))
    print('*'*50)
    return dict_output

def getFileCoOccurence(categ_file, hash_script_file): 
    print(categ_file)
    hash_script_df_full        = pd.read_csv(hash_script_file)  
    all_scripts = np.unique(hash_script_df_full['FILE'].tolist())
    dict_output = analyzeCommitsForCoOccurence(categ_file)
    print('*'*50)
    for k_, v_ in dict_output.items():
        script_list = [] 
        for hash_ in v_:
            hash_df      = hash_script_df_full[hash_script_df_full['HASH']==hash_]
            hash_scripts = list( np.unique( hash_df['FILE'].tolist() ) )
            script_list  = script_list + hash_scripts
        script_list =  list( np.unique( script_list ) )
        fil_pop = round( (float(len(script_list))/float(len(all_scripts)) ) * 100, 5)
        print('{} categories of defects observed for {}% scripts (script proportion)'.format(k_, fil_pop))
    print('*'*50)
    return dict_output

def getDefectProportionPerCategory(categ_f):
    # Carrega o arquivo se for um caminho
    if isinstance(categ_f, str):
        categ_df = pd.read_csv(categ_f)
    else:
        categ_df = categ_f
    
    categ_df['CHANGED_CATEG'] = categ_df['CATEG'].apply(changeCategIfNeeded)
    total_commits = categ_df['HASH'].nunique()
    defect_df = categ_df[categ_df['CHANGED_CATEG'] != 'NO_DEFECT']
    total_defect_commits = defect_df['HASH'].nunique()
    commits_per_categ = defect_df.groupby('CHANGED_CATEG')['HASH'].nunique()

    print('Defect Proportion per category (% of all commits that contain the category):')
    for categ, count in commits_per_categ.items():
        prop = round((count / total_commits) * 100, 5)
        print(f'{categ}: {prop}%')

    total_defect_prop = round((total_defect_commits / total_commits) * 100, 5)
    print(f'Total Defects (% of all commits): {total_defect_prop}%')
    print(f'Total number of defect commits: {total_defect_commits}')
    print('='*50)
    
def getDefectProportionPerSubCategory(categ_f, output_csv_path=None, category_prefixes=None, category_label=None):
    if isinstance(categ_f, str):
        categ_df = pd.read_csv(categ_f, low_memory=False)
    else:
        categ_df = categ_f.copy()

    if category_prefixes:
        categ_df = categ_df[categ_df['CATEG'].str.startswith(tuple(category_prefixes))]

    total_commits = categ_df['HASH'].nunique()
    defect_df = categ_df[categ_df['CATEG'] != 'NO_DEFECT']
    total_defect_commits = defect_df['HASH'].nunique()
    commits_per_categ = defect_df.groupby('CATEG')['HASH'].nunique()

    print('Defect Proportion per subcategory (% of all commits that contain the subcategory):')
    results = []
    for categ, count in commits_per_categ.items():
        prop = round((count / total_commits) * 100, 5)
        print(f'{categ}: {prop}%')
        results.append({
            'CATEGORY': categ,
            'TOTAL_COMMITS_WITH_CATEGORY': count,
            'PROPORTION_OVER_ALL_COMMITS (%)': prop,
            'MACRO_CATEGORY': category_label if category_label else ''
        })

    total_defect_prop = round((total_defect_commits / total_commits) * 100, 5)
    print(f'Total Defects (% of all commits): {total_defect_prop}%')
    print(f'Total number of defect commits: {total_defect_commits}')
    print('='*50)

    if output_csv_path:
        pd.DataFrame(results).to_csv(output_csv_path, index=False)
        print(f'CSV File Generated: {output_csv_path}')

if __name__=='__main__': 
    hash_mapping_file  = '/home/aluno/Documentos/resultados/company1-all-repos/csv/acid-output/REPLICATION_HASH_CATEG.csv'
    categ_output_file = '/home/aluno/Documentos/resultados/PIPr/csv/acid-output/REPLICATION_CATEG_OUTPUT_FINAL.csv'
    
    getFileDist(categ_output_file, hash_mapping_file) 
    getDefectProportionPerCategory(categ_output_file)

    getDefectProportionPerSubCategory(
        categ_f=categ_output_file,
        output_csv_path='/home/aluno/Documentos/resultados/PIPr/csv/acid-output/REPLICATION_CONFIG_SUB_CATEG_OUTPUT_FINAL.csv',
        category_prefixes=['CD_'],
        category_label='CONFIGURATION'
    )

    getDefectProportionPerSubCategory(
        categ_f=categ_output_file,
        output_csv_path='/home/aluno/Documentos/resultados/PIPr/csv/acid-output/REPLICATION_SERVICE_SUB_CATEG_OUTPUT_FINAL.csv',
        category_prefixes=['SERVICE_'],
        category_label='SERVICE'
    )
    

    getFileCoOccurence(categ_output_file, hash_mapping_file)
