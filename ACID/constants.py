'''
Akond Rahman 
Mar 19, 2019 
ACID: Store configuration strings and cosntants here 
'''
import diff_parser

DATASET_DIR  = 'dataset' 
REPO_FILE_LIST = 'eligible_repos.csv'
MASTER_BRANCH  = 'main' 
FILE_READ_MODE = 'r' 
AST_PATH = 'EXTRA_AST' 
PP_EXTENSION = '.pp'
IAC_FILES = [
    "Pulumi.yaml", "Pulumi.yml", "cdk.json", "cdktf.json",
    ".py", ".go", ".js", ".ts", ".java", ".tf",
    ".cs", ".fs", ".vb", ".cpp", ".kt", ".php", ".rb", ".swift", ".abap", ".edn"
]
DATE_TIME_FORMAT = "%Y-%m-%dT%H-%M-%S"
WHITE_SPACE  = ' '
TAB = '\t'
NEWLINE = '\n'
HASH_SYMBOL = '#'
comments_elems = ['#', '//', '/*', '*/']
CSV_REPLICATION = '/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/replication/iac_time_period.csv'
CSV_DEFAULT_PATH = '/home/aluno/filtered-repositories-iac-criteria/criteria4/'

CHANGE_DIR_CMD = 'cd '
GIT_COMM_CMD_1 = "git show --name-status "
GIT_COMM_CMD_2 = " | awk '/(Pulumi\\.yaml|Pulumi\\.yml|cdk\\.json|cdktf\\.json|\\.py|\\.go|\\.js|\\.ts|\\.java|\\.tf|\\.cs|\\.fs|\\.vb|\\.cpp|\\.kt|\\.php|\\.rb|\\.swift|\\.abap|\\.edn)/ {print $2}'"
BASH_CMD = 'bash'
BASH_FLAG = '-c'
GIT_SHOW_CMD = "git show"
GIT_DIFF_CMD = " git diff"
HG_REV_SPECL_CMD   = " ; hg log -p -r " 

ENCODING = 'utf8'
UTF_ENCODING = 'utf-8'
FILE_WRITE_MODE = 'w'
SPACY_ENG_DICT  = 'en_core_web_sm'
ROOT_TOKEN = 'ROOT'

STR_LIST_BOUNDS  = 3 # tri-grams 
NO_DEFECT_CATEG        = 'NO_DEFECT'
BUGGY_COMMIT           = 'BUGGY_COMMIT'
prem_bug_kw_list      = ['error', 'bug', 'fix', 'issu', 'mistake', 'incorrect', 'fault', 'defect', 'flaw', 'solve' ]

CONFIG_DEFECT_CATEG    = 'CONFIG_DATA_DEFECT'
config_defect_kw_list       = ['value', 'config', 'option',  'setting', 'hiera', 'data']

DEP_DEFECT_CATEG       = 'DEP_DEFECT'
dep_defect_kw_list    =     ['requir', 'depend', 'relation', 'order', 'sync', 'compatibil', 'ensur',  'inherit']
dep_defect_kw_list    +=    ['version', 'deprecat', 'packag', 'path', 'modul', 'upgrad', 'updat']
dep_xtra_kw_list       = ['module']

# Retirado import por causa de port em network
# These are used on diff_parser
VAR_SIGN = '='
ATTR_SIGN = '=>'
diff_depen_code_elems = ['~>' , '::', 'include', 'packag', 'exec', 'require', 'import', 'version']

DOC_DEFECT_CATEG      = 'DOC_DEFECT'
# origal author doc_defect_kw_list    =     ['doc', 'comment', 'spec', 'license', 'copyright', 'notice', 'header', 'readme'] 
# changed made removing 'spec' and header
doc_defect_kw_list    =     ['doc', 'comment', 'licens', 'copyright', 'notic', 'readm'] 
doc_defect_kw_list    +=    ['descript']

IDEM_DEFECT_CATEG     = 'IDEM_DEFECT'
idem_defect_kw_list   =     ['idempot']
idem_defect_kw_list   +=    ['determin']

diff_idem_code_elem    = 'class' 
diff_idem_removal_cnt  = 10 

CONDI_DEFECT_CATEG     = 'CONDITIONAL_DEFECT'
logic_defect_kw_list  =     ['logic', 'condition', 'bool']

diff_logic_code_elems = ['if' , 'unless', 'els', 'case']
diff_logic_code_elems+= ['while', 'elif']

SECU_DEFECT_CATEG           = 'SECURITY_DEFECT'
secu_defect_kw_list         =     ['vulner', 'ssl', 'secr', 'authent', 'password', 'security', 'cve']
# secu_defect_kw_list         +=    ['cert', 'firewall', 'encrypt', 'protect']
# adding access to control
secu_defect_kw_list         +=    ['cert', 'firewall', 'encrypt', 'protect', 'access']

diff_secu_code_elems        = ['tls', 'cert', 'cred', 'ssl', 'password', 'pass', 'pwd'] 

NETWORK_DEFECT_CATEG        = 'CD_NETWORK_DEFECT'
# removing address that was from the original author
# network_defect_kw_list      = ['network', 'address', 'port', 'tcp', 'dhcp', 'ssh', 'gateway', 'connect']
network_defect_kw_list      = ['network', 'port', 'tcp', 'dhcp', 'ssh', 'gateway', 'connect']
network_defect_kw_list     += ['rout']
diff_network_elems          = ['url', 'vpc', 'subnet', 'endpoint']
network_extra_kw_list       = ['gateway']
# ip tem que sair por causa de descrIPt em doc

STORAGE_DEFECT_CATEG        = 'CD_STORAGE_DEFECT'
storage_defect_kw_list      = ['sql', 'db', 'databas', 'disk']
storage_extra_kw_list       = ['disk']
# retirar database por causa de data em configuration

CACHE_DEFECT_CATEG          = 'CD_CACHE_DEFECT'
cache_defect_kw_list        = ['cach', 'memory', 'buffer', 'evict', 'ttl']

CREDENTIALS_DEFECT_CATEG    = 'CD_CREDENTIAL_DEFECT'
credentials_defect_kw_list  = ['polic', 'credential', 'iam', 'role', 'token', 'user', 'usernam', 'password']
credentials_extra_kw_list   = ['polic']
diff_credentials_kw_list    = ['polic', 'credential']

FILE_SYSTEM_DEFECT_CATEG    = 'CD_FILE_SYSTEM_DEFECT'
file_system_defect_kw_list  = ['file', 'permiss']

SYNTAX_DEFECT_CATEG    = 'SYNTAX_DEFECT'
syntax_defect_kw_list    = ['compil', 'lint', 'warn', 'typo', 'spell', 'indent', 'regex', 'duplicat', 'variabl', 'whitespac']
syntax_defect_kw_list   += ['type', 'format', 'naming', 'casing', 'styl', 'comma', 'pattern', 'quot']
# retirar name por causa de username

SERVICE_RESOURCE_DEFECT_CATEG        = 'SERVICE_RESOURCE_DEFECT'
resource_defect_kw_list     = ['servic', 'server', 'location', 'resourc', 'provi', 'cluster']
resource_xtra_kw_list       = ['kube','cloud']
diff_service_code_elems     = ['service'] 

SERVICE_PANIC_DEFECT_CATEG          = 'SERVICE_PANIC_DEFECT'
panic_defect_kw_list = ['check', 'deploy', 'reboot', 'build', 'mount', 'kernel', 'extran', 'bypass']

CLASSIFICATION_PARSE = [
    (CONDI_DEFECT_CATEG,            logic_defect_kw_list,       diff_parser.checkDiffForLogicDefects),
    (IDEM_DEFECT_CATEG,             idem_defect_kw_list,        None),
    (DOC_DEFECT_CATEG,              doc_defect_kw_list,         diff_parser.checkDiffForDocDefects),
    (SYNTAX_DEFECT_CATEG,           syntax_defect_kw_list,      None),
    (SECU_DEFECT_CATEG,             secu_defect_kw_list,        diff_parser.checkDiffForSecurityDefects),
    (DEP_DEFECT_CATEG,              dep_defect_kw_list,         diff_parser.checkDiffForDepDefects),
    (CONFIG_DEFECT_CATEG,           config_defect_kw_list,      diff_parser.checkDiffForConfigDefects),
    (NETWORK_DEFECT_CATEG,          network_defect_kw_list,     diff_parser.checkDiffForNetwork),
    (STORAGE_DEFECT_CATEG,          storage_defect_kw_list,     None),
    (CACHE_DEFECT_CATEG,            cache_defect_kw_list,       None),
    (FILE_SYSTEM_DEFECT_CATEG,      file_system_defect_kw_list, None),
    (CREDENTIALS_DEFECT_CATEG,      credentials_defect_kw_list, diff_parser.checkDiffForCredentials),
    (SERVICE_RESOURCE_DEFECT_CATEG, resource_defect_kw_list,    diff_parser.checkDiffForServiceDefects),
    (SERVICE_PANIC_DEFECT_CATEG,    panic_defect_kw_list,       None)
]

EXTRA_FIX_KEYWORD     = 'fix'   
EXTRA_BUG_KEYWORD     = 'bug'   

DFLT_KW         = 'default'
CLOSE_KW        = 'closes-bug'
MERGE_KW        = 'merge' 
REVERT_KW       = 'revert'
REVERT_REGEX    = r'^revert.*\".*\"'

IDEM_XTRA_KW    = 'idempot' # for detectBuggyCommit() 

LOGIC_XTRA_KW1  = 'condit'
LOGIC_XTRA_KW2  = 'logic'
LOGIC_XTRA_KW3  = 'bool' 

SYNTAX_XTRA_KW1 = 'lint'
SYNTAX_XTRA_KW2 = 'typo' 
SYNTAX_XTRA_KW4 = 'syntax'
syxtax_xtra_kw_list = ['lint', 'typo', 'syntax','type']
DOC_XTRA_KW     = 'notice' 
# DEPEND_XTRA_KW  = 'override' 
# NETWORK_XTRA_KW = 'provis'

diff_config_code_elems = ['hiera' , 'hash', 'parameter']

diff_extra_idem_elems  = ['ensure', 'unless', 'creates', 'replace'] 

lev_cutoff = 75

'''
Oracle dataset work 
'''
ORACLE_HASH_CHECKLIST = ['75e460ab929a76e9e4a8d42740a529b3a476e952', 
                         '9a5a540738f887f87886ae4f9f52d5ade1b26bc7', 
                         '0d834093814b3d184eff36b2835530a847ee6421', 
                         '854e0e7b9fc339dc56bf3e2b3de7107c3f35b835', 
                         'a7dedf197a24bf8a3fad00d1d1f58eede2f43057',
                         '114536ef2e7c569300019844e0ca57d278e27791'
                        ]