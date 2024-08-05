import os
from config import config
import logging
import logging.handlers


class LoggerClass:
    def __init__(self, logger_name):
        self.pool = dict()
        self.config = dict()
        self.config['log'] = config.LOG
        self.path = self.config['log']['folder'] + self.config['log'][str(logger_name) + '_file']

        try:
            os.stat(self.config['log']['folder'])
        except FileNotFoundError:
            print('------------------------------------------------------------------')
            print('[ERROR] Error writing log at %s' % self.path)
            print('[ERROR] Please verify path folder exits')
            print('------------------------------------------------------------------')
            exit()

        try:
            self.logger = logging.getLogger(logger_name)
            loggerHandler = logging.handlers.TimedRotatingFileHandler(filename=self.path, when='midnight', interval=1,
                                                                      backupCount=int(self.config['log']['days_for_rotate']))
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            loggerHandler.setFormatter(formatter)
            self.logger.addHandler(loggerHandler)
            self.logger.setLevel(logging.DEBUG)
        except PermissionError:
            print('------------------------------------------------------------------')
            print('[ERROR] Error writing log at %s' % self.path)
            print('[ERROR] Please verify write permissions')
            print('------------------------------------------------------------------')
            exit()

    def get_logger(self):
        return self.logger
