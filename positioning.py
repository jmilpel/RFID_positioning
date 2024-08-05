import pika
import pika.exceptions
import time
import os
from concurrent.futures import ThreadPoolExecutor
from config import config
from logger import logs
from ujson import decode
from core import position


BROKER = config.BROKER
WORKER = config.WORKER
logger_main = logs.get_logger_main()
logger_msg = logs.get_logger_msg()


def workflow(channel, method_frame, header_frame, body):
    try:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        json_received = decode(body)
        position.manage_data(msg=json_received)
    except Exception as error:
        logger_main.error('Error managing msg %s: %s', str(body), str(error))


def queue_consumer(broker):
    while True:
        pid = os.getpid()
        try:
            exchange = BROKER['exchange']
            credentials = pika.PlainCredentials(username=broker['username'], password=broker['password'])
            parameters = pika.connection.ConnectionParameters(host=broker['host'], port=int(broker['port']), virtual_host=broker['virtual_host'], credentials=credentials)
            connection = pika.BlockingConnection(parameters=parameters)
            channel = connection.channel()
            logger_main.info('[%d] Successfully connected!!! Start messages consumption...', pid)
            channel.basic_consume(queue=exchange, on_message_callback=workflow)
            try:
                channel.start_consuming()
            except pika.exceptions.AMQPChannelError as error:
                logger_main.error('[%d] Error at broker channel: %s. Retying in %d seconds', pid, str(error), int(broker['retry_connection_sleep']))
                channel.stop_consuming()
                connection.close()
                time.sleep(int(broker['retry_connection_sleep']))
                continue
            except Exception as error:
                logger_main.error('[%d] Error at broker connection: %s. Retying in %d seconds', pid, str(error), int(broker['retry_connection_sleep']))
                continue
        except pika.exceptions.AMQPConnectionError as error:
            logger_main.error('[%d] Error at broker connection: %s. Retying in %d seconds', pid, str(error), int(broker['retry_connection_sleep']))
            time.sleep(int(BROKER['retry_connection_sleep']))
            continue
        except Exception as error:
            logger_main.error('[%d] Error at broker channel: %s. Retying in %d seconds', pid, str(error), int(broker['retry_connection_sleep']))
            time.sleep(int(BROKER['retry_connection_sleep']))
            continue


if __name__ == "__main__":
    max_workers = int(WORKER['max_workers'])

    logger_main.info("Starting %d broker consumer processes...", max_workers)
    executor = ThreadPoolExecutor(max_workers=max_workers)
    for i in range(max_workers):
        executor.submit(queue_consumer, BROKER)
        time.sleep(int(BROKER['sharding_sleep']))
    logger_main.info('All consumers are running now!!')
