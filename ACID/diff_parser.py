'''
Akond Rahman 
Mar 20, 2019 
Diff Parser that looks at diff content 
'''
#reff: https://github.com/cscorley/whatthepatch
import whatthepatch

import constants

from fuzzywuzzy import fuzz

import re

# [(1, None, '# == Class cdh4::pig'), (None, 1, '# == Class cdh::pig'), (2, 2, '#'), (3, None, '# Installs and configures Apache Pig.'), (None, 3, '# Installs and configures Apache Pig and Pig DataFu.'), (4, 4, '#'), (5, None, 'class cdh4::pig {'), (6, None, "  package { 'pig':"), (7, None, "    ensure => 'installed',"), (8, None, '  }'), (None, 5, 'class cdh::pig('), (None, 6, "    $pig_properties_template = 'cdh/pig/pig.properties.erb',"), (None, 7, "    $log4j_template          = 'cdh/pig/log4j.properties.erb',"), (None, 8, ')'), (None, 9, '{'), (None, 10, '    # cdh::pig requires hadoop client and configs are installed.'), (None, 11, "    Class['cdh::hadoop'] -> Class['cdh::pig']"), (9, 12, ''), (10, None, "  file { '/etc/pig/conf/pig.properties':"), (11, None, "    content => template('cdh4/pig/pig.properties.erb'),"), (12, None, "    require => Package['pig'],"), (13, None, '  }'), (None, 13, "    package { 'pig':"), (None, 14, "        ensure => 'installed',"), (None, 15, '    }'), (None, 16, "    package { 'pig-udf-datafu':"), (None, 17, "        ensure => 'installed',"), (None, 18, '    }'), (None, 19, ''), (None, 20, '    $config_directory = "/etc/pig/conf.${cdh::hadoop::cluster_name}"'), (None, 21, '    # Create the $cluster_name based $config_directory.'), (None, 22, '    file { $config_directory:'), (None, 23, "        ensure  => 'directory',"), (None, 24, "        require => Package['pig'],"), (None, 25, '    }'), (None, 26, "    cdh::alternative { 'pig-conf':"), (None, 27, "        link    => '/etc/pig/conf',"), (None, 28, '        path    => $config_directory,'), (None, 29, '    }'), (None, 30, ''), (None, 31, '    file { "${config_directory}/pig.properties":'), (None, 32, '        content => template($pig_properties_template),'), (None, 33, "        require => Package['pig'],"), (None, 34, '    }'), (None, 35, '    file { "${config_directory}/log4j.properties":'), (None, 36, '        content => template($log4j_template),'), (None, 37, "        require => Package['pig'],"), (None, 38, '    }'), (14, 39, '}')]

def parseTheDiff(diff_text):
    parse_out_dict = {}
    diff_mess_str = str(diff_text) ## changes for Python 3 migration 
    for diff_ in whatthepatch.parse_patch(diff_mess_str):
        all_changes_line_by_line = diff_[1] ## diff_ is a tuple, changes is idnetified by the second index 
        line_numbers_added, line_numbers_deleted = [], [] 
        add_dic, del_dic = {}, {}
        parse_out_dict   = {}
        for change_tuple in all_changes_line_by_line:
            if (change_tuple[0] != None ):
                line_numbers_added.append(change_tuple[0])
                add_dic[change_tuple[0]] = change_tuple[2]
            if (change_tuple[1] != None ):
                line_numbers_deleted.append(change_tuple[1])                
                del_dic[change_tuple[1]] = change_tuple[2]
        lines_changed = list(set(line_numbers_added).intersection(line_numbers_deleted)) 
        for line_number in lines_changed:
            if ((line_number in add_dic) and (line_number in del_dic)):
                parse_out_dict[line_number] = [ del_dic[line_number], add_dic[line_number]] ## <removed content, added cotnent>
        #print parse_out_dict
    return parse_out_dict

def filterTextList(txt_lis):
    return_list = []
    return_list = [x_.lower() for x_ in txt_lis if  constants.HASH_SYMBOL not in x_ ]
    return_list = [x_.replace(constants.TAB, '') for x_ in return_list ]    
    return_list = [x_.replace(constants.NEWLINE, '') for x_ in return_list ] 
    return_list = [x_ for x_ in return_list if len(x_) > 1 ]        
    return return_list

def getAddDelLines(diff_mess):
    added_text, deleted_text = [], []
    diff_mess_str = str(diff_mess)
    try:
        for diff_ in whatthepatch.parse_patch(diff_mess_str):
            all_changes_line_by_line = getattr(diff_, "changes", None)

            if all_changes_line_by_line:
                for change in all_changes_line_by_line:
                    if change.new is not None:
                        added_text.append(change.line)

                    if change.old is not None:
                        deleted_text.append(change.line) 

    except Exception as e:
        print(f"[ERROR] Error when processing diff: {e}")

    return added_text, deleted_text

def getSpecialConfigDict(text_str_list, splitter):
    dic2ret = {}
    for x_ in text_str_list:
        if (splitter in x_):
            _key_ = x_.replace(constants.WHITE_SPACE, '').split(splitter)[0] 
            _val_ = x_.replace(constants.WHITE_SPACE, '').split(splitter)[-1] 
            if _key_ not in dic2ret:
                dic2ret[_key_] = _val_
    # print text_str_list
    # print dic2ret
    return dic2ret

def filterConfig(oldValue):
    oldValue = oldValue.replace(",","")
    oldValue = oldValue.replace("'","")
    oldValue = oldValue.replace(";","")
    val_     = oldValue.replace(">","")

    return val_ 

def getConfigChangeCnt(start_dict, end_dict):
    tracker = 0 
    track_list = []
    val_track_list = []
    for k_, v_ in start_dict.items():
        if (k_ in end_dict ) and (k_ not in track_list) and (v_ not in val_track_list) and (len(v_) > 1): 
            oldValue     = end_dict[k_] 
            newValue     = v_ 
            # need more pre processign ugh 
            oldValue = filterConfig(oldValue) 
            newValue = filterConfig(newValue)
            if newValue != oldValue:
                # print k_
                # print oldValue, newValue
                tracker = tracker + 1 
        track_list.append(k_)
        val_track_list.append(v_) 
    # print '>'*5
    return tracker 

def checkDiffForConfigDefects(diff_text):
    added_text , deleted_text = [], []
    final_flag = False 
    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)
    config_change_tracker = 0 

    valu_assi_dict_addi = getSpecialConfigDict(added_text, constants.VAR_SIGN)
    valu_assi_dict_deli = getSpecialConfigDict(deleted_text, constants.VAR_SIGN)
 
    attr_assi_dict_addi = getSpecialConfigDict(added_text, constants.ATTR_SIGN)
    attr_assi_dict_deli = getSpecialConfigDict(deleted_text, constants.ATTR_SIGN)

    # config_change_tracker = getConfigChangeCnt(valu_assi_dict_addi, valu_assi_dict_deli) + getConfigChangeCnt(valu_assi_dict_deli, valu_assi_dict_addi) + getConfigChangeCnt(attr_assi_dict_addi, attr_assi_dict_deli) + getConfigChangeCnt( attr_assi_dict_deli, attr_assi_dict_addi)
    config_change_tracker = getConfigChangeCnt(valu_assi_dict_addi, valu_assi_dict_deli) + getConfigChangeCnt(attr_assi_dict_addi, attr_assi_dict_deli)

    if config_change_tracker > 0 :
        final_flag = True 


    return final_flag

def checkDiffForDepDefects(diff_text):
    added_text , deleted_text = [], []
    final_flag, final_flag_1, final_flag_2 = False , False, False 
    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)
    added_text   = [x_ for x_ in added_text if constants.VAR_SIGN not in x_ ]
    added_text   = [x_ for x_ in added_text if constants.ATTR_SIGN not in x_ ]

    deleted_text   = [x_ for x_ in deleted_text if constants.VAR_SIGN not in x_ ]
    deleted_text   = [x_ for x_ in deleted_text if constants.ATTR_SIGN not in x_ ]
    # print added_text, deleted_text
    added_text   = [z_ for z_ in added_text if any(x_ in z_ for x_ in constants.diff_depen_code_elems ) ]
    deleted_text = [z_ for z_ in deleted_text if any(x_ in z_ for x_ in constants.diff_depen_code_elems ) ] 

    if (len(added_text) > 0 ) and (len(deleted_text) > 0 ) :
       final_flag = True 

    return final_flag

import re

def has_comment(line):
    # ignore if it's a string
    if re.fullmatch(r'\s*["\'].*["\']\s*', line.strip()):
        return False

    # line's entire comment
    if re.search(r'^\s*(#|//).+', line):
        return True
    
    # inline comment
    if re.search(r'[^"\']*(#|//).+', line):
        return True

    # blocks comment
    if re.search(r'/\*.*?\*/', line, re.DOTALL):
        return True

    return False

def checkDiffForDocDefects(diff_text):
    lines_changed = []
    final_flag = False 
    diff_mess_str = str(diff_text) ## changes for Python 3 migration 
    for diff_ in whatthepatch.parse_patch(diff_mess_str):
        all_changes_line_by_line = diff_[1] 
        line_numbers_added, line_numbers_deleted = [], [] 
        if all_changes_line_by_line is not None:
            for change_tuple in all_changes_line_by_line:
                content = change_tuple[2] 
                content = content.replace(constants.WHITE_SPACE, '')
                if change_tuple[0] is not None and has_comment(content):
                    line_numbers_added.append(content)
                if change_tuple[1] is not None and has_comment(content):
                    line_numbers_deleted.append(content)                
        lines_changed = list(set(line_numbers_added).intersection(line_numbers_deleted)) 
        # print lines_changed
    lines_changed = [x_ for x_ in lines_changed if len(x_) > 1 ]
    if len(lines_changed) > 0:
        final_flag = True
    return final_flag

def checkDiffForNetwork(diff_text):
    added_text, deleted_text = [], []
    final_flag = False 
    added_text, deleted_text = getAddDelLines(diff_text)

    added_text = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)

    added_text = [line for line in added_text if any(keyword in line for keyword in constants.diff_network_elems)]
    deleted_text = [line for line in deleted_text if any(keyword in line for keyword in constants.diff_network_elems)]

    if added_text or deleted_text:
        final_flag = True

    return final_flag

def checkDiffForCredentials(diff_text):
    added_text, deleted_text = [], []
    final_flag = False 
    added_text, deleted_text = getAddDelLines(diff_text)

    added_text = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)

    added_text = [line for line in added_text if any(keyword in line for keyword in constants.diff_credentials_kw_list)]
    deleted_text = [line for line in deleted_text if any(keyword in line for keyword in constants.diff_credentials_kw_list)]

    if added_text or deleted_text:
        final_flag = True

    return final_flag
    
def checkDiffForLogicDefects(diff_text):
    added_text , deleted_text = [], []
    final_flag, final_flag_1, final_flag_2 = False , False, False 
    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)
    added_text   = [x_ for x_ in added_text if constants.VAR_SIGN not in x_ ]
    added_text   = [x_ for x_ in added_text if constants.ATTR_SIGN not in x_ ]

    deleted_text   = [x_ for x_ in deleted_text if constants.VAR_SIGN not in x_ ]
    deleted_text   = [x_ for x_ in deleted_text if constants.ATTR_SIGN not in x_ ]
    # print added_text, deleted_text
    added_text   = [z_ for z_ in added_text if any(x_ in z_ for x_ in constants.diff_logic_code_elems ) ]
    deleted_text = [z_ for z_ in deleted_text if any(x_ in z_ for x_ in constants.diff_logic_code_elems ) ] 

    if (len(added_text) > 0 ) or (len(deleted_text) > 0 ) :
       final_flag = True 
    return final_flag
        
def checkDiffForSecurityDefects(diff_text):
    final_flag = False     
    added_text , deleted_text = [], []

    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)
    added_text   = [x_ for x_ in added_text if constants.VAR_SIGN  in x_ ]
    added_text   = [x_ for x_ in added_text if constants.ATTR_SIGN  in x_ ]

    deleted_text = [x_ for x_ in deleted_text if constants.VAR_SIGN  in x_ ]
    deleted_text = [x_ for x_ in deleted_text if constants.ATTR_SIGN  in x_ ]

    added_text   = [x_.split(constants.VAR_SIGN)[0].replace(constants.WHITE_SPACE, '') for x_ in added_text]
    added_text   = [x_.split(constants.ATTR_SIGN )[0].replace(constants.WHITE_SPACE, '') for x_ in added_text] 

    deleted_text   = [x_.split(constants.VAR_SIGN)[0].replace(constants.WHITE_SPACE, '') for x_ in deleted_text]
    deleted_text   = [x_.split(constants.ATTR_SIGN )[0].replace(constants.WHITE_SPACE, '') for x_ in deleted_text]    

    added_text   = [z_ for z_ in added_text if any(x_ in z_ for x_ in constants.diff_secu_code_elems ) ]
    deleted_text = [z_ for z_ in deleted_text if any(x_ in z_ for x_ in constants.diff_secu_code_elems ) ]    
    # print added_text, deleted_text
    if (len(added_text) > 0) or (len(deleted_text) > 0): 
        final_flag = True
    return final_flag
            
def checkDiffForServiceDefects(diff_text):
    final_flag = False 
    added_text , deleted_text = [], []

    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)
    added_text   = [x_ for x_ in added_text if constants.VAR_SIGN  not in x_ ]
    added_text   = [x_.lower() for x_ in added_text if constants.ATTR_SIGN not in x_ ]

    deleted_text = [x_ for x_ in deleted_text if constants.VAR_SIGN not in x_ ]
    deleted_text = [x_.lower() for x_ in deleted_text if constants.ATTR_SIGN not in x_ ]

    added_text   = [z_ for z_ in added_text if any(x_ in z_ for x_ in constants.diff_service_code_elems) ]
    deleted_text = [z_ for z_ in deleted_text if any(x_ in z_ for x_ in constants.diff_service_code_elems) ] 

    if (len(added_text) > 0 ) and (len(deleted_text) > 0 ) :
       final_flag = True 
    return final_flag

def matchStringsFuzzily(add_str_lis, del_str_lis):
    # takes two sring as input, returns levesjhteins's ratio, reff: https://www.datacamp.com/community/tutorials/fuzzy-string-python
    add_str = constants.WHITE_SPACE.join(add_str_lis)
    del_str = constants.WHITE_SPACE.join(del_str_lis) 
    lower_add_str = add_str.lower() 
    lower_del_str = del_str.lower()
    lev_str_ratio = fuzz.token_sort_ratio( lower_add_str, lower_del_str  ) ## this is levenshteien ratio, in a sorted manner 
    return lev_str_ratio


def checkDiffForSyntaxDefects(diff_text):
    final_flag = False 
    added_text , deleted_text = [], []
    attr_added_text , attr_deleted_text = [], []
    var_added_text , var_deleted_text = [], []

    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)

    '''
    look for variable name change 
    '''
    attr_added_text   = [x_.lower() for x_ in added_text if constants.ATTR_SIGN in x_ ]
    var_added_text    = [x_.lower().replace(constants.WHITE_SPACE, '') for x_ in added_text if constants.VAR_SIGN in x_ ]

    attr_deleted_text = [x_.lower() for x_ in deleted_text if constants.ATTR_SIGN in x_ ]
    var_deleted_text  = [x_.lower().replace(constants.WHITE_SPACE, '') for x_ in deleted_text if constants.VAR_SIGN in x_ ]
    '''
    Now compare 
    '''

    # if (len(added_text)) and (len(deleted_text)): ## wrong logic 
    if ((len(attr_added_text)) == (len(attr_deleted_text))) or (len(var_added_text) == len(var_deleted_text) ) : ## right logic , same number of additions and deletiosn for variables 
        final_flag = True 
    elif ( (matchStringsFuzzily(attr_added_text, attr_deleted_text) > constants.lev_cutoff ) or (matchStringsFuzzily(var_added_text, var_deleted_text) > constants.lev_cutoff ) ):
        # Why does the original author uses minus?
        # final_flag - True 
        final_flag = True


    return final_flag



def checkDiffForIdempotenceDefects(diff_text):
    final_flag = False 
    added_text , deleted_text = [], []

    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)

    added_text = [x_ for x_ in added_text if constants.diff_idem_code_elem in x_ ] 
    if (len(added_text) == 1) or (len(deleted_text) > constants.diff_idem_removal_cnt):
       final_flag = True 

    return final_flag 

def checkDiffForIdemWithAttr(diff_text):
    final_flag = False 
    flag_list  = []
    added_text , deleted_text = [], []

    added_text, deleted_text = getAddDelLines(diff_text)
    added_text   = filterTextList(added_text)
    deleted_text = filterTextList(deleted_text)

    if(len(deleted_text) < len(added_text)):
        for text_ in added_text:
            for elem in constants.diff_extra_idem_elems:
                if elem in text_:
                    flag_list.append(True) 
    if (len(flag_list) > 0):    
        final_flag = True 
    return final_flag 
    