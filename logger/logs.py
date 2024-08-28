from logger import LoggerClass

if True:
    logger_main = LoggerClass.LoggerClass('main')
    logger_msg = LoggerClass.LoggerClass('msg')
    logger_rabbit = LoggerClass.LoggerClass('rabbit')
    # logger_mongo = LoggerClass.LoggerClass('mongo')


def get_logger_main():
    return logger_main.get_logger()


def get_logger_msg():
    return logger_msg.get_logger()


def get_logger_rabbit():
    return logger_rabbit.get_logger()


"""
def get_logger_errors():
    return logger_errors.get_logger()


def get_logger_mongo():
    return logger_mongo.get_logger()
"""
