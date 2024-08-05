import hashlib
from rabbitmq import rabbit
from config import config


RABBIT_REPORT = config.RABBIT_REPORT


class Report:
    """ Class client to publish messages at Delivery brokers
        Client will balance between all ports published at MQ Routing server (haproxy) with hash function device_id attendant """

    def __init__(self):
        """ Initialize with parameters configured at config file """
        RABBIT_REPORT['ports'] = RABBIT_REPORT['ports'] if isinstance(RABBIT_REPORT['ports'], list) else [str(RABBIT_REPORT['ports'])]
        size = len(RABBIT_REPORT['ports'])

        self.pool_publishers_size = size
        self.pool_publishers = []
        for port in RABBIT_REPORT['ports']:
            self.publisher = rabbit.Publisher(host=RABBIT_REPORT['host'], port=port)
            self.pool_publishers.append(self.publisher)

    def get_publisher(self, hash_key):
        """ Get publisher from publishers pool hash_key attendant """
        h = hashlib.sha1(str.encode(hash_key))
        index = int(h.hexdigest(), 16) % self.pool_publishers_size
        publisher = self.pool_publishers[index]
        return publisher

    def publish(self, msg):
        """ Publish message with publish method """
        hash_key = str(msg['msg_data']['tag_id'])
        publisher = self.get_publisher(hash_key=hash_key)
        publisher.publish(msg=msg, queue=RABBIT_REPORT['queue'])
