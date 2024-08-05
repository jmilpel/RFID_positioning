from config import config
from logger import logs
from ujson import encode
import pika
import pika.exceptions

logger = logs.get_logger_rabbit()

BROKER = config.BROKER


class Publisher:
    """ Class publisher for publish message at RabbitMQ broker
        We configure heartbeat according to broker configuration to keep the TCP connection established and channel"""

    def __init__(self, host, port):
        self.credentials = pika.PlainCredentials(username=BROKER['username'], password=BROKER['password'])
        self.parameters = pika.connection.ConnectionParameters(host=str(host), port=int(port), virtual_host=BROKER['virtual_host'], credentials=self.credentials)
        self.exchange = ''
        self.connection = None
        self.channel = None

    def connect(self, queue):
        """ Establish a new connection to RabbitMQ broker """
        if not self.connection or self.connection.is_closed:
            logger.info('-- Trying to establish a new connection... --')
            try:
                self.connection = pika.BlockingConnection(parameters=self.parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=queue, durable=True)
                logger.info('-- Successfully connected!! --')
            except Exception as e:
                logger.error('-- Error while establishing connection: %s --', str(e))
        elif not self.channel or self.channel.is_closed:
            logger.info('-- Trying to recover channel connection... ---')
            try:
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=queue, durable=True)
                logger.info('-- Successfully channel connected!! --')
            except Exception as e:
                logger.error('-- Error while recovering lost channel: %s --', str(e))

    def simple_publish(self, msg, queue):
        """ Simple publish message. It will be called from publish method"""
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=queue, body=encode(msg))
            logger.info('message sent: %s', msg)
        except Exception as e:
            msg['retry'] = msg['retry'] + 1 if 'retry' in msg else 1
            self.connection.close()
            self.publish(msg=msg, queue=queue)
            logger.info('-- Error publishing message %s at rabbit with simple_publish method: %s --', str(msg), str(e))

    def publish(self, msg, queue):
        """Publish msg, reconnecting if necessary"""
        if 'retry' not in msg or 'retry' in msg and msg['retry'] < int(BROKER['max_retries']):
            try:
                if not self.connection or self.connection.is_closed:
                    logger.info('-- Detected not connected or connection close --')
                    self.connect(queue=queue)
                elif not self.channel or self.channel.is_closed:
                    logger.info('-- Detected channel not connected or channel close --')
                    self.connect(queue=queue)
                self.simple_publish(msg=msg, queue=queue)

            except pika.exceptions.ConnectionClosed:
                logger.info('-- Error publishing message %s at rabbit: connection is closed --', str(msg))
                self.connect(queue=queue)
                self.simple_publish(msg=msg, queue=queue)
            except pika.exceptions.ChannelClosed:
                logger.info('-- Error publishing message %s at rabbit: channel is closed --', str(msg))
                self.connect(queue=queue)
                self.simple_publish(msg=msg, queue=queue)
            except pika.exceptions.AMQPConnectionError as e:
                logger.info('-- Error publishing message %s at rabbit. AMQP connection error: %s --', str(msg), str(e))
                self.connect(queue=queue)
                self.simple_publish(msg=msg, queue=queue)
            except pika.exceptions.AMQPChannelError as e:
                logger.info('-- Error publishing message %s at rabbit. AMQP channel error: %s --', str(msg), str(e))
                self.connect(queue=queue)
                self.simple_publish(msg=msg, queue=queue)
            except Exception as e:
                logger.info('-- Error publishing message %s at rabbit: %s --', str(msg), str(e))
                self.connect(queue=queue)
                self.simple_publish(msg=msg, queue=queue)
        else:
            logger.error('-- Max retries reached for msg %s --', str(msg))
