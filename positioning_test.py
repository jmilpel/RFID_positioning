import pika
from config import config
from logger import logs
from core import position
import time


BROKER = config.BROKER
WORKER = config.WORKER
logger_main = logs.get_logger_main()
logger_msg = logs.get_logger_msg()




# Función para procesar los mensajes de la cola
def procesar_mensaje(ch, method, properties, body):
    # Procesa el mensaje aquí
    msg = body.decode()
    logger_main.info(f'Mensaje recibido: {msg}')
    # Puedes agregar más lógica para procesar el mensaje según sea necesario
    position.manage_data(msg)
    time.sleep(0.2)


logger_main.info("Starting broker consumer processes...")
# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=BROKER['host'],
    port=BROKER['port'],
    credentials=pika.PlainCredentials(BROKER['username'], BROKER['password'])
))
channel = connection.channel()
if channel:
    logger_main.info('Consumer is running now!!')


# Declarar la cola
channel.queue_declare(queue=BROKER['queue'], durable=True)

# Conectar a la cola y comenzar a consumir mensajes
channel.basic_consume(
    queue=BROKER['queue'],
    on_message_callback=procesar_mensaje,
    auto_ack=True
)

print('Conectado a RabbitMQ y consumiendo mensajes...')
channel.start_consuming()