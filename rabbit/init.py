import os
import pika
from dotenv import load_dotenv
from pyrabbit.api import Client

load_dotenv(verbose=True)
# Создание Vhost
vh = os.getenv('RABBIT_VIRTUALHOST')
user = os.getenv('RABBIT_USER')
cl = Client(f"{os.getenv('RABBIT_HOST')}:{os.getenv('RABBIT_PORT_API')}", user, os.getenv('RABBIT_PASSWORD'))  #'guest', 'guest'
if vh not in cl.get_vhost_names():
	cl.create_vhost(vh)
cl.set_vhost_permissions(vh, user, '.*', '.*', '.*')

# создаем новую очередь на vhost, которые указываем в parameters (в данном случае test)
MQTT_credentials = pika.PlainCredentials(os.getenv('RABBIT_USER'), os.getenv('RABBIT_PASSWORD'))
MQTT_params = pika.ConnectionParameters(os.environ.get("RABBIT_HOST"), os.environ.get('RABBIT_PORT'), os.environ.get('RABBIT_VIRTUALHOST', default='/'), credentials=MQTT_credentials)
connection = pika.BlockingConnection(MQTT_params)
channel = connection.channel()
cnt = channel.queue_declare(queue=os.environ.get("RABBIT_QUEUE"), durable=True)

# exclusive -  то очередь будет разрешать подключаться только одному потребителю

# x-max-priority — разрешает сортировку по приоритетам в очереди с максимальным значением приоритета 255 (RabbitMQ версий 3.5.0 и выше). Число указывает максимальный приоритет, который будет поддерживать очередь. Если аргумент не установлен, очередь не будет поддерживать приоритет сообщений