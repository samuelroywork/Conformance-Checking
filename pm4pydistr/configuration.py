import os

ENVIRON_PREFIX = "pm4pydistr"
PARAMETERS_AUTO_HOST = "autohost"
PARAMETERS_AUTO_PORT = "autoport"

PARAMETER_USE_TRANSITION = "use_transition"
DEFAULT_USE_TRANSITION = False
PARAMETER_NO_SAMPLES = "no_samples"
DEFAULT_MAX_NO_SAMPLES = 10000000
PARAMETER_NUM_RET_ITEMS = "num_ret_items"
DEFAULT_MAX_NO_RET_ITEMS = 500

KEYPHRASE = "hello"
if str(os.name) == "posix":
    PYTHON_PATH = "python3"
else:
    PYTHON_PATH = "python"
BASE_FOLDER_LIST_OPTIONS = ["master"]

DEFAULT_TYPE = "slave"
THIS_HOST = "127.0.0.1"
PORT = 5001
MASTER_HOST = "127.0.0.1"
MASTER_PORT = 5001
CONF = "local"

PARAMETERS_TYPE = "type"
PARAMETERS_PORT = "port"
PARAMETERS_MASTER_HOST = "masterhost"
PARAMETERS_MASTER_PORT = "masterport"
PARAMETERS_CONF = "conf"
PARAMETERS_HOST = "host"
PARAMETERS_KEYPHRASE = "keyphrase"
PARAMETERS_BASE_FOLDERS = "basefolders"

SLEEPING_TIME = 30
SESSION_EXPIRATION = 70
