import datetime
import pytz
from utils import decorator
import time
import binascii
# import crc16


@decorator.catch_exceptions
def get_now_timestamp(time_precision='ms'):
    """ Get now timestamp"""
    if time_precision == 's':
        now = int(time.time())
    else:
        now = int(time.time()) * 1000
    return now


@decorator.catch_exceptions
def get_midnight_from_utc_timestamp(timestamp, timezone):
    """ Get UTC timestamp in seconds at 00:00 from UTC timestamp"""
    tz = pytz.timezone(timezone)
    date_utc = datetime.datetime.fromtimestamp(timestamp, tz)
    string_date_midnight = date_utc.strftime("%Y-%m-%d") + " 00:00:00"
    new_object = tz.localize(datetime.datetime.strptime(string_date_midnight, '%Y-%m-%d %H:%M:%S'))
    ts = (new_object - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return int(ts)


@decorator.catch_exceptions
def convert_utc_timestamp_to_date(timestamp, timezone):
    """ Convert UTC timestamp to date (year, month, day) timezone attendant.
        It returns a dict with {'year', 'month', 'day', 'hour', 'minute'} """
    tz = pytz.timezone(timezone)
    date = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    return {'year': date.year, 'month': date.month, 'day': date.day, 'hour': date.hour, 'minute': date.minute}


@decorator.catch_exceptions
def reverse(data):
    """ Reverse hex string in block of two characters """
    result = "".join([data[x:x + 2] for x in range(0, len(data), 2)][::-1])
    return result.upper()


@decorator.catch_exceptions
def convert_int_to_hex_string(number):
    """ Convert integer to hex string """
    return format(number, 'x')


@decorator.catch_exceptions
def convert_int_to_hex_string_with_length(number, length):
    """ Convert integer to hex string """
    str_hex = format(number, 'x')
    zero_added = length - len(str_hex)
    result = reverse('0'*zero_added + str_hex)
    return result


@decorator.catch_exceptions
def convert_str_to_hex_to_int(string):
    hex_bytes = bytes.fromhex(string)
    return int.from_bytes(hex_bytes, byteorder="big")


@decorator.catch_exceptions
def convert_hex_to_int(hex_value):
    return int(hex_value, 16)


@decorator.catch_exceptions
def convert_data_to_hexstring(data):
    return binascii.hexlify(data).decode()


@decorator.catch_exceptions
def convert_str_to_hex(string):
    return bytes.fromhex(string)


@decorator.catch_exceptions
def get_seconds_from_midnight(timestamp):
    """ Get UTC timestamp in seconds at 00:00 from UTC timestamp"""
    tz = pytz.timezone('UTC')
    date_utc = datetime.datetime.fromtimestamp(timestamp, tz)
    string_date_midnight = date_utc.strftime("%Y-%m-%d") + " 00:00:00"
    new_object = tz.localize(datetime.datetime.strptime(string_date_midnight, '%Y-%m-%d %H:%M:%S'))
    midnight_timestamp = int((new_object - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())
    return timestamp - midnight_timestamp


@decorator.catch_exceptions
def int_rssi(rssi):
    """ Returns the int RSSI value """
    return convert_str_to_hex_to_int(rssi) - 130
