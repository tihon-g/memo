import asyncio
import json
import psutil
import os, subprocess
from django.contrib.auth import get_user_model
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from .models import Order
from render.utils import execute_wait
User = get_user_model()

# def process_order(ch, method, properties, body):
#     # Функция для обработки сообщений rabbitmq
#     data = json.loads(body)
#     ch.basic_ack(delivery_tag=method.delivery_tag)
#     os.environ['RENDER_ORDER_ID'] = data['order_id']
#     print(f"process_order {os.environ['RENDER_ORDER_ID']}")
#     start_making_renders(data['order_id'], data['model'])
class ServerConsumer(AsyncConsumer):
    blenders = []
    active_orders = []
    async def websocket_connect(self, event):
        print('websocket_connect')
        await self.send({
            "type": "websocket.accept",
            #'message': final_message_data
        })
    async def websocket_receive(self, event): # websocket.receive
        message_data = json.loads(event['text'])
        print('websocket_connect', message_data)

    async def websocket_disconnect(self, event):
        # when the socket connects
        print('websocket_disconnect', event)

class RenderConsumer(AsyncConsumer):
    async def websocket_connect(self, event):

        # when the socket connects
        # self.kwargs.get("username")

        # https://channels.readthedocs.io/en/stable/topics/routing.html
        # Any captured groups will be provided in scope as the key url_route, a dict with a kwargs key containing a dict of the named regex groups and an args key with a list of positional regex groups.
        # Note that named and unnamed groups cannot be mixed: Positional groups are discarded as soon as a single named group is matched.
        kwargs = self.scope['url_route']['kwargs']
        #self.config = self.scope['url_route']['kwargs']['config']
        user = self.scope['user']
        #thread_obj = await self.get_thread(user, self.other_username)
        #self.chat_thread = thread_obj
        #self.room_group_name = thread_obj.room_group_name # group
        print('RenderConsumer: websocket_connect')
        # await self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        # self.rando_user = await self.get_name()
        await self.send({
            "type": "websocket.accept",
            #'message': final_message_data
        })

    async def websocket_receive(self, event): # websocket.receive
        message_data = json.loads(event['text'])
        print(f"RenderConsumer: websocket_receive: {event['text']}")
        if not os.getenv('BLENDER'):
            await self.send({
                "type": "websocket.send",
                "text": json.dumps({'msg': 'there is no blender installed'})
            })
            return
        cmd = [os.getenv('BLENDER'), '', '--background', '-noaudio', '--python', os.getenv('BLENDER_PY')]  # '--threads', '4',
        cmd[1] = os.path.join(settings.STATIC_ROOT, os.sep.join(message_data['model'].split('/')[1:]))

        print("!!>> cmd\n", cmd)
        print(f"----------RenderConsumer: call blender for {message_data['order']} ------------")
        os.environ['RENDER_ORDER_ID'] = message_data['order']
        for s in execute_wait(cmd):
            #print(s)
            if s.startswith('!! set worker:'):
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps({'worker': s.split(':')[1]})
                })
                continue
            if s.startswith('!!'):
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps({'msg': s})
                })
            if 'samples' in s:
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps({'progress': '/'.join(s.split('|')[-1].split(' ')[2:5:2])})
                })
            if s.startswith('!!saved'):
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps({'saved': s.split('|')[2]})
                })
        user = self.scope['user']
        username = "unknown"
        if user.is_authenticated:
            username = user.username
        message_data["user"] = username

        # save to db
        await self.send({
            "type": "websocket.send",
            "text": json.dumps({'ready': "ready!"})
        })
        #final_message_data = json.dumps(message_data)
        # await self.channel_layer.group_send(
        #     self.room_group_name, 1>
        #     {
        #         'type': 'chat_message',
        #         'message': final_message_data
        #     }
        # )

    async def broadcast_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": json.dumps({'msg': "Loading data please wait...", 'user': 'admin'})
        })
        await asyncio.sleep(15) ### chatbot? API -> another service --> response --> send
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    # async def chat_message(self, event):
    #     await self.send({
    #         "type": "websocket.send",
    #         "text": event['message']
    #     })

    async def websocket_disconnect(self, event):
        # when the socket connects
        print('websocket_disconnect', event)
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

    @database_sync_to_async
    def get_name(self):
        return User.objects.all()[0].username

    # @database_sync_to_async
    # def get_thread(self, user, other_username):
    #     return Thread.objects.get_or_new(user, other_username)[0]

    # @database_sync_to_async
    # def create_chat_message(self, user, message):
    #     thread = self.chat_thread
    #     return ChatMessage.objects.create(thread=thread, user=user, message=message)

    # @database_sync_to_async
    # def create_order(self, user, kind, rule, q):
    #     #thread = self.chat_thread
    #     return Order.objects.create(productkind=kind, rule=rule, quality=q)
