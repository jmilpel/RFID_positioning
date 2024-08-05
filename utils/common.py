import datetime
import pytz
import crc16
from utils import decorator
import time


@decorator.catch_exceptions
def get_now_timestamp(time_precision='ms'):
    """ Get now timestamp"""
    if time_precision == 's':
        now = int(time.time())
    else:
        now = int(time.time())* 1000
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
def calculate_woxu_checksum(data):
    """ calculate WOXU WIRELESS checksum for hex string """
    hex_checksum = convert_int_to_hex_string(crc16.crc16xmodem(bytes.fromhex(data)))
    result = reverse(hex_checksum)
    return result


@decorator.catch_exceptions
def encode_id(value_id, length):
    reverse_string = reverse(value_id)
    zero_size = length - len(reverse_string)
    result = reverse_string + '0'*zero_size
    return result
