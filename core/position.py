from utils import decorator, common  # constant
from logger import logs
from config import config
from rabbitmq import rabbitWss, rabbitReport
# import math
# import datetime

tags = dict()
logger = logs.get_logger_main()
logger_msg = logs.get_logger_msg()

enqueued_wss = rabbitWss.Wss()
enqueued_report = rabbitReport.Report()
RABBIT_WSS = config.RABBIT_WSS
RABBIT_REPORT = config.RABBIT_REPORT
TRACKING = config.TRACKING

last_tracking = dict()


"""
@decorator.catch_exceptions
def send_to_wss(json_tracking):
    if str(RABBIT_WSS['send_to_wss']).lower() == 'true':
        if 'date' in json_tracking:
            json_tracking.pop('date')
        json_wss = dict()
        json_wss['destiny'] = 'broadcast'
        json_wss['type'] = 0
        json_wss['data'] = json_tracking
        enqueued_wss.publish(msg=json_wss)
"""


"""
@decorator.catch_exceptions
def send_to_report(json_tracking):
    if str(RABBIT_REPORT['send_to_report']).lower() == 'true':
        if '_id' in json_tracking:
            json_tracking.pop('_id')
        if 'date' in json_tracking:
            json_tracking.pop('date')
        json_msg = dict()
        json_msg['msg_type'] = constant.ReportMsgType.TRACKING.value
        json_msg['msg_data'] = json_tracking
        enqueued_report.publish(msg=json_msg)
"""


"""
@decorator.catch_exceptions
def manage_location(msg_data):
    tag_id = msg_data['tag_id']
    anchor_id = msg_data['anchor_id']
    timestamp = msg_data['timestamp']
    seconds = msg_data['seconds']
    distance = msg_data['distance']
    battery = msg_data['battery']
    sos = msg_data['sos']
    if tag_id in tags:
        update_tag(tag_id=tag_id, anchor_id=anchor_id, seconds=seconds, timestamp=timestamp, distance=distance, 
                   battery=battery, sos=sos)
    else:
        initialize_tag(tag_id=tag_id, anchor_id=anchor_id, seconds=seconds, timestamp=timestamp, distance=distance, 
                       sos=sos)
"""



@decorator.catch_exceptions
def manage_data(msg):
    # print(msg)
    data = msg[0:2]
    if msg[0:2] == '15':
        # print('Trama para procesar, ', msg)
        process_epc_frame(msg)
    elif msg[0:2] == 18:
        pass
        # process_EPC_TID_frame(msg)


@decorator.catch_exceptions
def process_epc_frame(data):
    # This function can be used to process the data
    # For example, you can parse the data, store it in a database, etc.
    length = data[0:2]
    adr = data[2:4]
    cmd = data[4:6]
    status = data[6:8]
    ant = data[8:10]
    num = data[10:12]
    epc_length = data[12:14]
    # epc_final_bit = 14 + (epc_length * 2)
    epc_int_length = common.convert_str_to_hex_to_int(epc_length)
    epc = data[14:14 + (epc_int_length * 2)]
    rssi_hex = data[-14:-12]
    rssi = common.int_rssi(rssi_hex)
    crc16 = data[-12:-8]
    time = data[-8:]
    timestamp = common.convert_hex_to_int(time)

    json_msg = {'length': length, 'reader': adr, 'cmd': cmd, 'status': status, 'antenna': ant, 'num': num, 'epc': epc,
                'rssi': rssi, 'crc16': crc16, 'timestamp': timestamp}
    logger_msg.info('-->[TAG READ] %s', json_msg)
    # msg = compose_location_msg(json_msg=json_msg)
    # publish_msg(publisher=publisher, msg=msg)

    """print("LENGTH:", common.convert_str_to_hex_to_int(length), "- READER:", common.convert_str_to_hex_to_int(adr),
          "- CMD:", cmd, "- STATUS:", status, "- ANTENNA:", common.convert_str_to_hex_to_int(ant), "- NUM:", num,
          "- EPC:", epc, "- RSSI:", rssi, "- CRC16:", crc16, "- TIMESTAMP:", timestamp)  # functions.int_rssi(rssi)
    """
    print(json_msg)
    pass
