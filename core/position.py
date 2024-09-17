from utils import decorator, common  # constant
from logger import logs
from config import config
from rabbitmq import rabbitWss  # rabbitReport
# import datetime
# import math


tags = dict()
last_tag_inventory = dict()
logger = logs.get_logger_main()
logger_msg = logs.get_logger_msg()
logger_rabbit = logs.get_logger_rabbit()
enqueued_wss = rabbitWss.Wss()
# enqueued_report = rabbitReport.Report()
RABBIT_WSS = config.RABBIT_WSS
# RABBIT_REPORT = config.RABBIT_REPORT


def update_last_inventory(tag_epc, json_msg):
    """ Process the data to parse or stores in a database """
    last_tag_inventory[tag_epc] = json_msg
    # send_to_wss(json_msg)
    if json_msg['cmd'] == '01':
        logger_rabbit.info('-->[TAG INVENTORY] %s', json_msg)
        print(json_msg)


def check_last_inventory(json_last_inventory, json_msg, tag_epc):
    """ Check if the last tag inventory associated to the tag is duplicated or not in order to parse it"""
    # When timestamp is newer we update the inventory
    if json_msg['timestamp'] > json_last_inventory['timestamp']:
        update_last_inventory(tag_epc, json_msg)
    # When timestamp is the same but the rssi is better we update the inventory (reconsider this condition)
    elif json_msg['timestamp'] == json_last_inventory['timestamp']:
        if json_msg['rssi'] > json_last_inventory['rssi']:
            update_last_inventory(tag_epc, json_msg)
        """else:
            print('Duplicated')"""


@decorator.catch_exceptions
def process_msg(json_msg):
    """  Process the msg """
    tag_epc = json_msg['epc']
    if tag_epc not in last_tag_inventory:
        # json_tracking_1 = mongo.read_single_document(collection='TRACKING1', filter={'tag_id': tag_epc})
        # last_tracking[tag_epc] = json_msg
        update_last_inventory(tag_epc, json_msg)
    else:
        json_last_inventory = last_tag_inventory[tag_epc]
        check_last_inventory(json_last_inventory, json_msg, tag_epc)


@decorator.catch_exceptions
def check_antenna(ant):
    """ Returns the number of the antenna depends on the value """
    if ant == '01':
        return 1
    elif ant == '02':
        return 2
    elif ant == '04':
        return 3
    elif ant == '08':
        return 4


@decorator.catch_exceptions
def manage_data(msg):
    """ Detect the type of frame """
    # print(msg)
    data = msg[0:2]
    if data == '15':
        process_epc_frame(msg)
    elif data == 18:
        pass
        # process_EPC_TID_frame(msg)


@decorator.catch_exceptions
def process_error(msg):
    """ Detect the type of frame """
    # length = msg[0:2]
    # adr = msg[2:4]
    # cmd = msg[4:6]
    # status = msg[6:8]
    error_code = msg[8:10]
    if error_code == '00':
        print("Other errors")
    elif error_code == '03':
        print("Memory full, or illegal PC value")
    elif error_code == '04':
        print("Memory locked")
    elif error_code == '0b':
        print("Insufficient power supply")
    elif error_code == '0f':
        print("Undefined error")


@decorator.catch_exceptions
def process_inventory_frame(data):
    """ Process inventory dataframe to create its json and process it """
    # length = data[0:2]
    # adr = data[2:4]
    cmd = data[4:6]
    status = data[6:8]
    # ant = data[8:10]
    ant = check_antenna(data[8:10])
    # num = data[10:12]
    epc_length = data[12:14]
    # epc_final_bit = 14 + (epc_length * 2)
    epc_int_length = common.convert_str_to_hex_to_int(epc_length)
    epc = data[14:14 + (epc_int_length * 2)]
    rssi_hex = data[-22:-20]
    rssi = common.int_rssi(rssi_hex)
    # lsb_crc16 = data[-20:-18]
    # msb_crc16 = data[-18:-16]
    port_hex = data[-16:-8]
    time = data[-8:]
    client = common.convert_hex_to_str(port_hex)
    timestamp = common.convert_hex_to_int(time)
    json_msg = {'client': client, 'cmd': cmd, 'status': status, 'antenna': ant, 'epc': epc, 'rssi': rssi,
                'timestamp': timestamp}
    """json_msg = {'len': length, 'client': client, 'adr': adr, 'cmd': cmd, 'status': status, 'antenna': ant, 'num': num,
                'epc': epc, 'rssi': rssi, 'lsb-crc16': lsb_crc16, 'msb-crc16': msb_crc16, 'timestamp': timestamp}"""
    logger_msg.info('-->[TAG READ] %s', json_msg)
    process_msg(json_msg=json_msg)
    # msg = compose_location_msg(json_msg=json_msg)
    # publish_msg(publisher=publisher, msg=msg)


@decorator.catch_exceptions
def process_epc_frame(data):
    """ Read the cmd and status and classify the frames """
    # cmd = data[4:6]
    status = data[6:8]
    if status == '03':
        process_inventory_frame(data)
    elif status == 'fc':
        process_error(data)
    pass
