'''
Run script to get month wise defects 
Akond Rahman 
June 15, 2019 
'''

import numpy as np 
import pandas as pd 
import os 

categ_list     = ['SERVICE_DEFECT', 'SECURITY_DEFECT', 'DEP_DEFECT', 'DOC_DEFECT', 'CONFIG_DEFECT', 'SYNTAX_DEFECT', 'CONDITIONAL_DEFECT', 'IDEM_DEFECT']
invalid_months = []


def dumpContentIntoFile(strP, fileP):
    fileToWrite = open( fileP, 'w')
    fileToWrite.write(strP)
    fileToWrite.close()
    return str(os.stat(fileP).st_size)

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
                'SERVICE_PANIC_DEFECT': 'SERVICE_DEFECT'
                }
    if categ_param in mod_dict:
        categ_mod = mod_dict[categ_param]
    else:
        categ_mod = categ_param
    return categ_mod

def makeMonth(time_single_val):
    date_ = time_single_val.split('T')[0] 
    date_list = date_.split('-')
    month = date_list[0] + '-' + date_list[1] 
    return month 

def makeYear(time_single_val):
    date_     = time_single_val.split('T')[0] 
    date_list = date_.split('-')
    year      = date_list[0] 
    return year    


def changeCategForPlotting(categ_name):
    new_categ_dict = {
        'CONDITIONAL_DEFECT':'CONDITION', 
        # 'CONFIG_DEFECT':'CONFIG', 
        'CONFIG_DEFECT':'CONF_DATA', 
        'DEP_DEFECT':'DEPEND',
        'DOC_DEFECT':'DOCUMENT',
        'IDEM_DEFECT':'IDEMPOT',
        'SECURITY_DEFECT':'SECURITY',
        'SERVICE_DEFECT':'SERVICE', 
        'SYNTAX_DEFECT':'SYNTAX'
    }
    return new_categ_dict[categ_name] 

def makeMonthWiseDataset(file_name):
    str_builder  = ''
    acid_df  = pd.read_csv(file_name)
    acid_df['MONTH'] = acid_df['TIME'].apply(makeMonth)
    acid_df['CHANGED_CATEG'] = acid_df['CATEG'].apply(changeCategIfNeeded)
    # print acid_df.head() 
    acid_all_months =  np.unique( acid_df['MONTH'].tolist() ) 
    for per_month in acid_all_months: 
        if per_month not in invalid_months: 
            per_mon_df = acid_df[acid_df['MONTH']==per_month]
            per_mon_commits = np.unique( per_mon_df['HASH'].tolist() )
            commit_cnt  = len(per_mon_commits)
            per_mon_defect_hash = []
            for categ_ in categ_list: 
                per_mon_categ_df = per_mon_df[per_mon_df['CHANGED_CATEG']==categ_]
                per_categ_hashes = np.unique( per_mon_categ_df['HASH'].tolist() )
                categ_cnt = len(per_categ_hashes) 
                categ_perc = round(float(categ_cnt)/float(commit_cnt) , 5) * 100 
                str_builder = str_builder + per_month + ',' + changeCategForPlotting(categ_) + ',' + str(categ_perc) + '\n' 
                per_mon_defect_hash = per_mon_defect_hash + list(per_categ_hashes) 
            per_mon_defect_hash = np.unique(per_mon_defect_hash) 
            per_mon_defect_prop = round(float(len(per_mon_defect_hash))/float(commit_cnt), 5) * 100
            str_builder = str_builder + per_month + ',' + 'TOTAL' + ',' + str(per_mon_defect_prop) + '\n'
    dump_file_name =  '../../output/' + file_name.split('/')[-1].split('_')[0] + '_MONTH_TEMPORAL_FINAL.csv' 
    str_builder = 'MONTH,CATEG,CATEG_PERC' + '\n' + str_builder
    dumpContentIntoFile(str_builder, dump_file_name)

def makeYearWiseDataset(file_name):
    str_builder  = ''
    acid_df  = pd.read_csv(file_name)
    acid_df['YEAR'] = acid_df['TIME'].apply(makeYear)
    acid_df['CHANGED_CATEG'] = acid_df['CATEG'].apply(changeCategIfNeeded)
    # print acid_df.head() 
    acid_all_years =  np.unique( acid_df['YEAR'].tolist() ) 
    for per_year in acid_all_years: 
            per_year_df      = acid_df[acid_df['YEAR']==per_year]
            per_year_commits = np.unique( per_year_df['HASH'].tolist() )
            commit_cnt  = len(per_year_commits)
            per_year_defect_hash = []
            for categ_ in categ_list: 
                per_yr_categ_df  = per_year_df[per_year_df['CHANGED_CATEG']==categ_]
                per_categ_hashes = np.unique( per_yr_categ_df['HASH'].tolist() )
                categ_cnt = len(per_categ_hashes) 
                categ_perc = round(float(categ_cnt)/float(commit_cnt) , 5) * 100 
                str_builder = str_builder + per_year + ',' + changeCategForPlotting(categ_) + ',' + str(categ_perc) + '\n' 
                per_year_defect_hash = per_year_defect_hash + list(per_categ_hashes) 
            per_year_defect_hash = np.unique(per_year_defect_hash) 
            per_year_defect_prop = round(float(len(per_year_defect_hash))/float(commit_cnt), 5) * 100
            str_builder = str_builder + per_year + ',' + 'TOTAL' + ',' + str(per_year_defect_prop) + '\n' 
    dump_file_name =  '../../output/' + file_name.split('/')[-1].split('_')[0] + '_YEAR_TEMPORAL_FINAL.csv' 
    str_builder = 'YEAR,CATEG,CATEG_PERC' + '\n' + str_builder
    dumpContentIntoFile(str_builder, dump_file_name)
 


if __name__=='__main__':
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_OUTPUT_FINAL.csv'
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_OUTPUT_FINAL.csv'    
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_OUTPUT_FINAL.csv'
    # acid_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_OUTPUT_FINAL.csv'

    # tecnologias = ['TERRAFORM', 'PULUMI', 'AWS_CDK']
    # acid_output_file = '/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/replication/filter-acid-output/<INSERT_HERE>_REPLICATION_ONLY_CATEG_OUTPUT_FINAL.csv'
    # for tecnologia in tecnologias:
    #     acid_output = acid_output_file.replace("<INSERT_HERE>", tecnologia)
    #     makeYearWiseDataset(acid_output)
    #     makeMonthWiseDataset(acid_output)
    #     print(f"FINISHED {tecnologia}")
    acid_output_file = '/home/aluno/Documentos/resultados/company1-all-repos/csv/acid-output/COMPANY1CRITERIADOCFIX_CATEG_OUTPUT_FINAL.csv'
    # acid_output_file = '~/ACID-dataset/ARTIFACT/OUTPUT/REPLICATION_ONLY_CATEG_OUTPUT_FINAL.csv'
    makeMonthWiseDataset(acid_output_file)
    makeYearWiseDataset(acid_output_file)    