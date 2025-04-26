'''
Akond Rahman 
Dec 02, 2018 
Mar 19, 2019: ACID: Extractor 
'''
from    nltk.tokenize  import sent_tokenize
from    git            import Repo
import  os 
import  csv 
import  numpy as np
import  sys
import  subprocess
import  constants
import  classifier
import  ast
csv.field_size_limit(sys.maxsize)


def getEligibleProjects(fileNameParam):
  repo_list = []
  with open(fileNameParam, constants.FILE_READ_MODE) as f:
    reader = csv.reader(f)
    for row in reader:
      repo_list.append(row[0])
  return repo_list

def getPuppetFilesOfRepo(repo_dir_absolute_path):
    pp_, non_pp = [], []
    for root_, dirs, files_ in os.walk(repo_dir_absolute_path):
      for file_ in files_:
        full_p_file = os.path.join(root_, file_)
        if((os.path.exists(full_p_file)) and (constants.AST_PATH not in full_p_file) ):
#             if (full_p_file.endswith(constants.PP_EXTENSION)):
          if any(full_p_file.endswith(ext) for ext in constants.IAC_FILES):
            pp_.append(full_p_file)
    return pp_

def getRelPathOfFiles(all_pp_param, repo_dir_absolute_path):
  common_path = repo_dir_absolute_path
  files_relative_paths = [os.path.relpath(path, common_path) for path in all_pp_param]
  return files_relative_paths 

def getPuppRelatedCommits(repo_dir_absolute_path, ppListinRepo, branchName=constants.MASTER_BRANCH):
  mappedPuppetList=[]
  track_exec_cnt = 0
  repo_  = Repo(repo_dir_absolute_path)
  all_commits = list(repo_.iter_commits(branchName))
  for each_commit in all_commits:
    track_exec_cnt = track_exec_cnt + 1

    cmd_of_interrest1 = constants.CHANGE_DIR_CMD + repo_dir_absolute_path + " ; "
    cmd_of_interrest2 = constants.GIT_COMM_CMD_1 + str(each_commit)  +  constants.GIT_COMM_CMD_2
    cmd_of_interrest = cmd_of_interrest1 + cmd_of_interrest2
    commit_of_interest  = str(subprocess.check_output([constants.BASH_CMD, constants.BASH_FLAG, cmd_of_interrest])) #in Python 3 subprocess.check_output returns byte

    for ppFile in ppListinRepo:
      if ppFile in commit_of_interest:
        file_with_path = os.path.join(repo_dir_absolute_path, ppFile)
        mapped_tuple = (file_with_path, each_commit)
        mappedPuppetList.append(mapped_tuple)

  return mappedPuppetList

def IacRelatedCommits(repo_dir_absolute_path, iac_list_repo, branchName=constants.MASTER_BRANCH):
  mapped_iac_list = []
  track_exec_cnt  = 0
  repo_  = Repo(repo_dir_absolute_path)
  all_commits = list(repo_.iter_commits(branchName))
  for each_commit in all_commits:
    track_exec_cnt = track_exec_cnt + 1

    cmd_of_interrest1 = constants.CHANGE_DIR_CMD + repo_dir_absolute_path + " ; "
    cmd_of_interrest2 = constants.GIT_COMM_CMD_1 + str(each_commit)  +  constants.GIT_COMM_CMD_2
    cmd_of_interrest = cmd_of_interrest1 + cmd_of_interrest2
    commit_of_interest  = str(subprocess.check_output([constants.BASH_CMD, constants.BASH_FLAG, cmd_of_interrest])) #in Python 3 subprocess.check_output returns byte

    for iac_file in iac_list_repo:
      if iac_file in commit_of_interest:
        file_with_path = os.path.join(repo_dir_absolute_path, iac_file)
        mapped_tuple = (file_with_path, each_commit)
        mapped_iac_list.append(mapped_tuple)

  return mapped_iac_list

def getDiffStr(repo_path_p, commit_hash_p, file_p):
    cdCommand = f"{constants.CHANGE_DIR_CMD} {repo_path_p} ; "
    theFile = os.path.relpath(file_p, repo_path_p)
    
    diffCommand = f"{constants.GIT_SHOW_CMD} {commit_hash_p} -- {theFile}"
    command2Run = cdCommand + diffCommand

    diff_output = subprocess.check_output(
        [constants.BASH_CMD, constants.BASH_FLAG, command2Run]
    ).decode('utf-8')
    return diff_output

def makeDepParsingMessage(m_, i_): 
    upper, lower  = 0, 0
    lower = i_ - constants.STR_LIST_BOUNDS
    upper = i_ + constants.STR_LIST_BOUNDS 
    if upper > len(m_):
      upper = - 1 
    if lower < 0:
      lower = 0
    return constants.WHITE_SPACE.join(m_[i_ - constants.STR_LIST_BOUNDS : i_ + constants.STR_LIST_BOUNDS])

def processMessage(indi_comm_mess):
    splitted_messages = []
#   original
#    if ('*' in indi_comm_mess):
    if ('*' in indi_comm_mess) or (';' in indi_comm_mess):
      splitted_messages = indi_comm_mess.split('*')
      splitted_messages = indi_comm_mess.split(';')
    else:
      splitted_messages = sent_tokenize(indi_comm_mess)
    return splitted_messages 

def analyzeCommit(repo_path_param, iac_commits_mapping):
  verbose = False   # For oracle dataset it is True (later), otherwise it is False 
  pupp_bug_list = []
  all_commit_file_dict  = {}
  all_defect_categ_list = []
  hash_tracker = []
  for tuple_ in iac_commits_mapping:

    file_ = tuple_[0]
    commit_ = tuple_[1]
    msg_commit =  commit_.message 

    msg_commit = msg_commit.replace('\n', constants.WHITE_SPACE)
    msg_commit = msg_commit.replace(',',  ';')    
    msg_commit = msg_commit.replace('\t', constants.WHITE_SPACE)
    msg_commit = msg_commit.replace('&',  ';')  
    msg_commit = msg_commit.replace('#',  constants.WHITE_SPACE)
    msg_commit = msg_commit.replace('=',  constants.WHITE_SPACE)
    
    commit_hash = commit_.hexsha

    # '''
    # for testing purpose , uncomment only for tool accuracy purpose 
    # '''
    # if commit_hash in constants.ORACLE_HASH_CHECKLIST:
    #   verbose = True 
    # else:
    #   verbose = False 
    # '''
    # ''' 

    timestamp_commit = commit_.committed_datetime
    str_time_commit  = timestamp_commit.strftime(constants.DATE_TIME_FORMAT) ## date with time 

    #### categorization zone 
    per_commit_defect_categ_list = []
    if (commit_hash not in hash_tracker):
      bug_status, index_status = classifier.detectBuggyCommit(msg_commit, verbose) 
      # print bug_status 
      #if commit_hash == "1f03639bcddb66031b16ed6cfdf91f2bbdeca6c8":
        #bug_status = True
      if (bug_status) or (classifier.detectRevertedCommit(msg_commit) ):
        processed_message = processMessage(msg_commit)
        # each commit has multiple messages, need to merge them together in one list here, not in classifier 
        for tokenized_msg in processed_message:
            diff_content_str = getDiffStr(repo_path_param, commit_hash, file_)
            bug_categ = classifier.detectCateg(tokenized_msg, diff_content_str, verbose)
            # bug_categ = classifier.detectCategHashFounder(tokenized_msg, diff_content_str, verbose, hash=commit_hash)
            if len(bug_categ) == 0:
              per_commit_defect_categ_list.append(constants.BUGGY_COMMIT)
            else:
              per_commit_defect_categ_list += bug_categ
      else:
        per_commit_defect_categ_list  = [constants.NO_DEFECT_CATEG]

      bug_categ_list = np.unique(per_commit_defect_categ_list)
      '''
      for testing purpose , uncomment only for tool accuracy purpose 
      '''
      # if verbose:
      #   print bug_categ_list
      '''
      '''
      if (len(bug_categ_list) > 0):
        for bug_categ_ in bug_categ_list:      
            tup_ = (commit_hash, bug_categ_, file_, str_time_commit) 
            all_defect_categ_list.append(tup_)
            # -- my debug
            #if (tup_[1] != constants.NO_DEFECT_CATEG):
            #  print(tup_[1])
            # ---
            # print tup_[0], tup_[1], tup_[2], tup_[3]
            # print '-'*25
      else:    
        tup_ = (commit_hash, constants.NO_DEFECT_CATEG, file_, str_time_commit) 
        all_defect_categ_list.append(tup_)  
        
      hash_tracker.append(commit_hash) 
    #### file to hash mapping zone 
    if commit_hash not in all_commit_file_dict:
      all_commit_file_dict[commit_hash] = [file_]
    else:
      all_commit_file_dict[commit_hash]  = all_commit_file_dict[commit_hash] + [file_]    

  return all_commit_file_dict, all_defect_categ_list 

def getIacFilesOfRepo(repo_id, csv_file_path = constants.CSV_REPLICATION, csv_default = constants.CSV_DEFAULT_PATH):
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['id'] == str(repo_id):
                # Converter strings de listas para listas reais
                iac_paths = ast.literal_eval(row['iac_paths'])
                related_files = ast.literal_eval(row['related_files'])
                result = iac_paths + related_files
                result = [item.replace(csv_default + "/" + repo_id + '/', '') for item in result]
                return result
    return None, None

def getId(path):
  return path.split('/')[-1]

def runMiner(orgParamName, repo_name_param, branchParam, csv_file_path = None, csv_default = None):
  script_dir = os.path.dirname(os.path.abspath(__file__))
  repo_path   = script_dir + "/" + constants.DATASET_DIR + "/" + orgParamName + "/" + repo_name_param
  repo_branch = branchParam

  repo_id = getId(repo_path)
  all_iac_files_in_repo = getIacFilesOfRepo(repo_id, csv_file_path, csv_default)
  iac_commits_in_repo = IacRelatedCommits(repo_path, all_iac_files_in_repo, repo_branch)
  commit_file_dict, categ_defect_list = analyzeCommit(repo_path, iac_commits_in_repo)

  return commit_file_dict, categ_defect_list

  

def dumpContentIntoFile(strP, fileP):
  fileToWrite = open( fileP, constants.FILE_WRITE_MODE)
  fileToWrite.write(strP )
  fileToWrite.close()
  return str(os.stat(fileP).st_size)

