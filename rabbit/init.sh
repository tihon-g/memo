#!/bin/sh

# Create Rabbitmq user
( rabbitmqctl wait --timeout 60 $RABBIT_PID_FILE ; \
rabbitmqctl add_user $RABBIT_USER $RABBIT_PASSWORD 2>/dev/null ; \
rabbitmqctl set_user_tags $RABBIT_USER administrator ; \
rabbitmqctl set_permissions -p / $RABBIT_USER  ".*" ".*" ".*" ; \
echo "*** User '$RABBIT_USER' with password '$RABBIT_PASSWORD' completed. ***" ; \
echo "*** Log in the WebUI at port 15672 (example: http://localhost:15672) ***") &


# https://khashtamov.com/ru/celery-best-practices/
# https://webdevblog.ru/asinhronnye-zadachi-v-django-s-redis-i-celery/
# https://khashtamov.com/ru/how-to-deploy-django-app/

#$ sudo rabbitmqctl add_user myuser mypassword
#$ sudo rabbitmqctl add_vhost myvhost
#$ sudo rabbitmqctl set_user_tags myuser mytag
#$ sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"


#sudo scutil --set HostName myhost.local
#Then add that host name to /etc/hosts so it’s possible to resolve it back into an IP address:
#127.0.0.1       localhost myhost myhost.local

#sudo rabbitmqctl status

# $@ is used to pass arguments to the rabbitmq-server command.
# For example if you use it like this: docker run -d rabbitmq arg1 arg2,
# it will be as you run in the container rabbitmq-server arg1 arg2
rabbitmq-server $@


#broker_url = 'amqp://myuser:mypassword@localhost:5672/myvhost'

# django-rabbitmq 0.1.3 - Start a RabbitMQ consumer after django server start.


# Переходим к реализации
# Чтобы начать работать с Rabbit, нам не нужно никаких суперприблуд, нужен банальный composer.
# Пуллим из Docker образ и запускаем его. Советую пуллить по тегу 3-management.
# По этому тегу будет доступен крайний стабильный релиз RabbitMQ; приписка management означает,
# что он будет поставлен вместе с панелью администрирования в виде Web UI
# (пользовательский интерфейс, представленный в виде сайта, который запускается в web-браузере).


# Запуск RabbitMQ с помощью Docker
#
#RabbitMQ совместим не со всеми версиями Linux Debian, поэтому я использовала Docker. Для целей обучения и тестирования — этого вполне достаточно.
#
#Запускаем RabbitMQ:
#
#
#1
#docker run --hostname localhost -p 8080:5672 -p 15672:15672 rabbitmq:3-management
#Я сопоставила порт 8080 на своей машине и порт RabbitMQ — 5672. Это означает, что мои скрипты будут обращаться по адресу localhost:8080 для того, чтоб получить или отправить сообщение в очередь. Вы можете назначить другие номера портов.
#
#Вторая связка — 15672:15672 — для сопоставления порта RabbitMQ, используемого для обращения к веб-интерфейсу и порта 15672 на локальной машине. Для доступа к веб-интерфейсу в строке браузера потребуется указать адрес http://localhost:15672.
#
#Если при запуске контейнера порты не указать — обращение к RabbitMQ окажется невозможным.
#
#По умолчанию для доступа к RabbitMQ используются логин/пароль: guest/guest .


# URLParameters — класс позволяет передавать URL-адрес AMQP при создании объекта и поддерживает хост, порт, виртуальный хост, ssl, имя пользователя и пароль в базовом URL-адресе, а другие параметры передаются через параметры запроса.

#import pika
#
#parameters = pika.URLParameters('amqp://guest:guest@rabbit-server1:5672/%2F')


# Поместить сообщение в очередь
#import pika
#
#credentials = pika.PlainCredentials('guest', 'guest')
#connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',
#                                                               8080,
#                                                               '/',
#                                                               credentials))
#channel = connection.channel()
#
## Если очередь с указанным именем не существует, queue_declare() создаст ее
#channel.queue_declare(queue='my_queue')
#
## Имя очереди должно быть определено в параметре routing_key
#channel.basic_publish(exchange='', routing_key='my_queue', body="Hello World!")
#
#connection.close()

# http://dev-lab.info/2019/03/работа-с-rabbitmq-в-python-с-чего-начать/
