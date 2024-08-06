import os
from configobj import ConfigObj

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = ConfigObj(os.path.join(BASE, 'config.cfg'))

LOG = CONFIG['log']
BROKER = CONFIG['broker']

WORKER = CONFIG['worker']
RABBIT_WSS = CONFIG['rabbit_wss']
RABBIT_REPORT = CONFIG['rabbit_report']
TRACKING = CONFIG['tracking']
# MONGO = CONFIG['mongo']
# WOXU = CONFIG['woxu']


LOG_FOLDER = LOG['folder']
LOG_DAYS_FOR_ROTATE = LOG['days_for_rotate']
LOG_MAIN_FILE = LOG['main_file']
LOG_MSG_FILE = LOG['msg_file']
LOG_RABBIT_FILE = LOG['rabbit_file']
# LOG_MONGO_FILE = LOG['mongo_file']