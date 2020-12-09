# -*- coding: utf-8 -*-

import json
import os
import subprocess
import socket
import pika
import time


# config_name = "queue.ini"
# try:
#     config = configparser.ConfigParser()
#     config.read(config_name)
# except FileNotFoundError:
#     print(f"Config file {config_name} haven't found!")
#     exit()

# state = {}
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# print(BASE_DIR)
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
# BLENDER = os.path.join(config['RENDER_MACHINE']['INSTALL_DIR'], config['RENDER_MACHINE']['PROCESS'])
# CAMERA_QUALITY = {'size_x': 1250, 'size_y': 1000, 'focus': 75, 'angle_0': 60, 'angle_3': 15}
# POSTIN = {}


def execute_wait(com):
    proc = subprocess.Popen(com, shell=False, stdout=subprocess.PIPE, universal_newlines=True)
    # windows Warning : Using shell = True can be a security hazard
    # Note Do not use stdout=PIPE or stderr=PIPE with this function as that can deadlock based on the child process output volume. Use Popen with the communicate() method when you need pipes.
    # subprocess.run(["ls", "-l", "/dev/null"], capture_output=True)
    for stdout_line in iter(proc.stdout.readline, ""):
        yield stdout_line
    proc.stdout.close()
    return_code = proc.wait()
    if return_code:
        print(f"proc failed - {subprocess.CalledProcessError(return_code, com)}")


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
        MQTT_params = pika.ConnectionParameters(os.environ.get("RABBIT_HOST"), os.environ.get('RABBIT_PORT'), '/', credentials=MQTT_credentials)
        connection = pika.BlockingConnection(MQTT_params)
        channel = connection.channel()
        # берем из очереди только 1 сообщение
        channel.basic_qos(prefetch_count=1)
        print('[*] Waiting for messages. To exit press CTRL+C')
        channel.basic_consume('orders', process_order)
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
        model3d = os.path.join(os.getenv('DJANGO_BASE_DIR'), model)
        cmd = [os.getenv('BLENDER'), model3d, '--background', '-noaudio', '--python', os.getenv('BLENDER_PY')]  #'--threads', '4',
        print("!!>> cmd\n", cmd)
        print(f"** call blender for {order} **")
        for s in execute_wait(cmd):
            print(s)
    except Exception as err:
        print(f'{repr(err)}')

def parsing(s):
    if s.startswith('!!'):
        print(s[2:])


# # it is special for docker commented
# os.environ['RABBIT_USER'] = 'django'
# os.environ['RABBIT_PASSWORD'] = 'memo'
# os.environ['RABBIT_HOST'] = '127.0.0.1'
# os.environ['RABBIT_PORT'] = '5672'
# os.environ['QUALITY'] = '5'
# os.environ['DJANGO_BASE_DIR'] = '/home/arsen/memo/rendering'

from dotenv import load_dotenv
load_dotenv()
os.environ['RENDER_MACHINE'] = 'Air [MacOS]'
print('queue.py started')
if __name__ == "__main__":
    main()

