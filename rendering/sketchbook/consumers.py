import os

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

from furniture.models import ProductKind
from render.models import Order, Quality


class SketchbookConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.group_name = 'sketchbook'

        await self.channel_layer.group_add(group=self.group_name, channel=self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def render_created(self, event):
        if event['order_id'] == self.scope['session']['order_waiting']:
            await self.send_json({'type': 'render_created', 'event': event})

    @database_sync_to_async
    def create_order(self, data):
        order = Order()
        order.created_by = self.scope['user']
        order.kind_id = data['kind']
        order.quality_id = Quality.objects.first().id
        order.rule = ';'.join([f'{part_name}:{finish}' for part_name, finish in data['parts'].items()])
        order.running = False
        order.save()
        return order.id

    @database_sync_to_async
    def check_if_render_exists(self, product_kind_id, parts):
        kind = ProductKind.objects.get(id=product_kind_id)
        print([f'{part}:{finish}' for part, finish in parts.items()])
        filename = kind.parse_rules([f'{part}:{finish}' for part, finish in parts.items()], only_one=True)
        if 'file' not in filename:
            print(filename)
            return False, None

        path = os.path.join(str(kind.product.id), '1', f'{filename["file"]}.jpg')  # TODO quality hardcoded
        return os.path.exists(os.path.join(settings.MEDIA_ROOT, path)), path

    async def receive_json(self, data, **kwargs):
        if data['type'] == 'get_render':
            exists, path = await self.check_if_render_exists(data['kind'], data['parts'])
            if exists:
                await self.send_json({'type': 'render_created', 'event': {'render_path': settings.MEDIA_URL + path}})
            else:
                order_id = await self.create_order(data)
                self.scope['session']['order_waiting'] = order_id

