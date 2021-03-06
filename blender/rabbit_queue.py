# -*- coding: utf-8 -*-

import json
import os
import subprocess
import socket
import pika
import time
from render.utils import execute_wait

def main():
    pingcounter = 0
    isreachable = False
    while not isreachable and pingcounter < 30:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f'trying to connect to mqtt {os.getenv("RABBIT_HOST")}... {pingcounter}', end='\r')
            s.connect((os.getenv("RABBIT_HOST"), int(os.environ.get('RABBIT_PORT'))))
            isreachable = True
        except socket.error as e:
            time.sleep(2)
            pingcounter += 1
        s.close()

    if isreachable:
        print(f"{os.environ.get('RABBIT_PORT')} is reachable!")
        MQTT_credentials = pika.PlainCredentials(os.environ.get("RABBIT_USER"), os.environ.get("RABBIT_PASSWORD"))
        MQTT_params = pika.ConnectionParameters(os.environ.get("RABBIT_HOST"), os.environ.get('RABBIT_PORT'), os.environ.get('RABBIT_VIRTUALHOST', default='/'), credentials=MQTT_credentials)
        connection = pika.BlockingConnection(MQTT_params)
        channel = connection.channel()
        # берем из очереди только 1 сообщение
        channel.basic_qos(prefetch_count=1)
        print('[*] Waiting for messages. To exit press CTRL+C')
        channel.basic_consume(os.environ.get('RABBIT_QUEUE'), process_order)
        channel.start_consuming()


def process_order(ch, method, properties, body):
    # Функция для обработки сообщений rabbitmq
    data = json.loads(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    os.environ['RENDER_ORDER_ID'] = data['order_id']
    print(f"process_order {os.environ['RENDER_ORDER_ID']}")
    start_making_renders(data['order_id'], data['model'])

def start_making_renders(order, model):
    try:
        #model3d = os.path.join(os.getenv('DJANGO_BASE_DIR'), model)
        cmd = [os.getenv('BLENDER'), model, '--background', '-noaudio', '--python', os.getenv('BLENDER_PY')]  #'--threads', '4',
        print("!!>> cmd\n", cmd)
        print(f"** call blender for {order} **")
        for s in execute_wait(cmd):
            print(parsing(s))
    except Exception as err:
        print(f'{repr(err)}')

def parsing(s):
    if s.startswith('!!'):
        print(s[2:])


from dotenv import load_dotenv
load_dotenv()

print(f"rabbit_queue.py {os.environ['RENDER_MACHINE']} started")
if __name__ == "__main__":
    main()

