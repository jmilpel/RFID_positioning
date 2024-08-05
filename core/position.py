from utils import decorator, constant, common
from logger import logs
from config import config
from rabbitmq import rabbitWss, rabbitReport
import math
import datetime

tags = dict()
logger = logs.get_logger_main()
logger_msg = logs.get_logger_msg()

enqueued_wss = rabbitWss.Wss()
enqueued_report = rabbitReport.Report()
RABBIT_WSS = config.RABBIT_WSS
RABBIT_REPORT = config.RABBIT_REPORT
TRACKING = config.TRACKING

last_tracking = dict()


@decorator.catch_exceptions
def compose_tag_config(anchor_id, tag_id, first_slot_time, first_slot_slot):
    header = constant.PacketHeader.TAGCONFIG.value
    length = constant.PacketLength.TAGCONFIG.value
    anchor_id = common.encode_id(value_id=anchor_id, length=16)
    subtype = '03'
    sequence = '07'
    slot_number = '01'
    tag_id = common.encode_id(value_id=tag_id, length=16)
    test_per_period = '0A00'
    first_slot_time = common.convert_int_to_hex_string_with_length(number=first_slot_time, length=2)
    first_slot_slot = common.convert_int_to_hex_string_with_length(number=first_slot_slot, length=4)
    period = '01'
    rsv = '0000'
    result = (header + length + anchor_id + subtype + sequence + slot_number + tag_id + test_per_period + first_slot_time + first_slot_slot + period + rsv).upper()
    crc = common.calculate_woxu_checksum(data=result)
    result = result + crc
    return result


@decorator.catch_exceptions
def process_data(tag_id, anchor_id, seconds, timestamp, distance, battery, sos):
    distances = tags[tag_id]['distances']
    sos = tags[tag_id]['sos'] or sos
    if seconds % 120 == 0:
        logger.info('Tags check: ' + str(tags))
    if len(distances.keys()) >= int(WOXU['min_anchor_for_location']):
        means = dict()
        for _anchor_id in distances:
            mean = algorithm.z_score_filter(distances=distances[_anchor_id])
            if mean:
                means[_anchor_id] = mean
        point = algorithm.trilateration(means=means)
        save_tracking(tag_id=tag_id, timestamp=timestamp, point=point, battery=battery, sos=sos)
        logger.info('tag %s - position %s', tag_id, str(point))
    initialize_tag(tag_id=tag_id, anchor_id=anchor_id, seconds=seconds, timestamp=timestamp, distance=distance, sos=sos)


@decorator.catch_exceptions
def save_tracking(tag_id, timestamp, point, battery, sos):
    json_tracking = dict()
    json_tracking['timestamp'] = timestamp
    json_tracking['date'] = datetime.datetime.utcfromtimestamp(timestamp)
    json_tracking['tag_id'] = tag_id
    json_tracking['battery'] = battery
    json_tracking['x'] = point[0]
    json_tracking['y'] = point[1]
    json_tracking['sos'] = sos

    if tag_id not in last_tracking:
        json_tracking_1 = mongo.read_single_document(collection='TRACKING1', filter={'tag_id': tag_id})
        last_tracking[tag_id] = json_tracking
    else:
        json_tracking_1 = last_tracking[tag_id]
        last_tracking[tag_id] = json_tracking

    if not json_tracking_1:
        mongo.write_single_document(collection='TRACKING1', document=json_tracking.copy())
        if str(TRACKING['save_tracking']).lower() == 'true':
            mongo.write_single_document(collection='TRACKING', document=json_tracking.copy())
        send_to_wss(json_tracking=json_tracking)
        send_to_report(json_tracking=json_tracking)
    else:
        tracking_1_x = json_tracking_1['x']
        tracking_1_y = json_tracking_1['y']
        tracking_1_timestamp = json_tracking_1['timestamp']
        distance_km = math.sqrt(pow(point[0] - tracking_1_x, 2) + pow(point[1] - tracking_1_y, 2)) / 100000
        speed_kmh = (distance_km*3600) / (json_tracking['timestamp'] - tracking_1_timestamp)
        if speed_kmh <= int(WOXU['max_speed_filter']):
            mongo.update_single_document(collection='TRACKING1', filter={'tag_id': tag_id}, document=json_tracking.copy(), upsert=True)
            if str(TRACKING['save_tracking']).lower() == 'true':
                mongo.write_single_document(collection='TRACKING', document=json_tracking.copy())
            send_to_wss(json_tracking=json_tracking)
            send_to_report(json_tracking=json_tracking)

    if sos:
        mongo.write_single_document(collection='ALERT', document=json_tracking.copy())


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


@decorator.catch_exceptions
def check_distance(msg):
    result = True
    distance = msg['distance']
    if distance > int(TRACKING['max_distance']):
        logger.info("Filtered tramma by distance: %s" % msg)
        result = False
    return result


@decorator.catch_exceptions
def initialize_anchor(tag_id, anchor_id, distance, sos):
    tags[tag_id]['distances'][anchor_id] = [distance]
    tags[tag_id]['sos'] = sos


@decorator.catch_exceptions
def update_anchor(tag_id, anchor_id, distance, sos):
    tags[tag_id]['distances'][anchor_id].append(distance)
    tags[tag_id]['sos'] = sos


@decorator.catch_exceptions
def initialize_tag(tag_id, anchor_id, seconds, timestamp, distance, sos):
    tags[tag_id] = {'timestamp': timestamp, 'seconds': seconds, 'distances': {anchor_id: [distance]}, 'sos': sos}


@decorator.catch_exceptions
def update_tag(tag_id, anchor_id, seconds, timestamp, distance, battery, sos):
    tag_id_seconds = tags[tag_id]['seconds'] if seconds >= tags[tag_id]['seconds'] else 0
    if seconds - tag_id_seconds >= int(WOXU['seconds_interval']):
        process_data(tag_id=tag_id, anchor_id=anchor_id, seconds=seconds, timestamp=timestamp, distance=distance, battery=battery, sos=sos)
        process_anchor_activity(anchor_id=anchor_id)
    else:
        if anchor_id in tags[tag_id]['distances']:
            update_anchor(tag_id=tag_id, anchor_id=anchor_id, distance=distance, sos=sos)
        else:
            initialize_anchor(tag_id=tag_id, anchor_id=anchor_id, distance=distance, sos=sos)


@decorator.catch_exceptions
def process_anchor_activity(anchor_id):
    now_timestamp = common.get_now_timestamp()
    if json_anchors_last_activity:
        if str(anchor_id) in json_anchors_last_activity:
            anchor_last_timestamp = json_anchors_last_activity[str(anchor_id)]
            if now_timestamp % int(WOXU['anchor_refresh_time']) < anchor_last_timestamp % int(WOXU['anchor_refresh_time']):
                json_anchors_last_activity[str(anchor_id)] = common.get_now_timestamp()
                anchor_document = mongo.read_single_document(collection='ANCHOR', filter={'anchor_id': anchor_id})
                if anchor_document['last_heartbeat'] < now_timestamp:
                    mongo.update_single_document(collection='ANCHOR', filter={'_id': anchor_document['_id']}, document={'last_heartbeat': now_timestamp})
                    logger.info('Update last_heartbeat from TRACKING in ANCHOR: %s', str(anchor_id))
            else:
                json_anchors_last_activity[str(anchor_id)] = common.get_now_timestamp()
        else:
            json_anchors_last_activity[str(anchor_id)] = common.get_now_timestamp()
    else:
        all_anchors = mongo.read_multi_document(collection='ANCHOR', filter={})
        for json_anchor in all_anchors:
            mongo_anchor_id = json_anchor['anchor_id']
            if mongo_anchor_id == anchor_id:
                json_anchors_last_activity[str(anchor_id)] = common.get_now_timestamp()
                break


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
        update_tag(tag_id=tag_id, anchor_id=anchor_id, seconds=seconds, timestamp=timestamp, distance=distance, battery=battery, sos=sos)
    else:
        initialize_tag(tag_id=tag_id, anchor_id=anchor_id, seconds=seconds, timestamp=timestamp, distance=distance, sos=sos)


@decorator.catch_exceptions
def manage_data(msg):
    if check_distance(msg):
        manage_location(msg_data=msg)
    logger_msg.info('[LOCATION] %s', str(msg))
