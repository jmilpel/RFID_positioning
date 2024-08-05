import logging.handlers
from config import config

LOG_FOLDER = config.LOG_FOLDER
LOG_FILE = config.LOG_RABBIT_FILE
DAYS_FOR_ROTATE = int(config.LOG_DAYS_FOR_ROTATE)
LOG = LOG_FOLDER + LOG_FILE


try:
    logger = logging.getLogger('rabbit')
    loggerHandler = logging.handlers.TimedRotatingFileHandler(filename=LOG, when='midnight', interval=1, backupCount=DAYS_FOR_ROTATE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    loggerHandler.setFormatter(formatter)
    logger.addHandler(loggerHandler)
    logger.setLevel(logging.DEBUG)
except OSError as error:
    print('------------------------------------------------------------------')
    print('[ERROR] Error writing log at %s' % LOG)
    print('[ERROR] Please verify path folder exits and write permissions')
    print('------------------------------------------------------------------')
    exit()


def get_logger():
    """ Return an instance of logger to write log at dispatcher.log file """
    return logger
