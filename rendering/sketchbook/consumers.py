import os

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

from furniture.models import ProductKind
from render.models import Order, Quality
from django.core.cache import cache


RENDER_ORDER_KEY = 'sketchbook_render_order_id_{}'
CURRENT_ORDER_KEY = 'sketchbook_current_order_{}'


class SketchbookConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def render_created(self, event):
        await self.send_json({'type': 'render_created', 'event': event})

    async def render_progress(self, event):
        await self.send_json({'type': 'render_progress', 'event': event})

    async def render_error(self, event):
        await self.send_json({'type': 'render_error', 'event': event})

    @database_sync_to_async
    def create_order(self, data):
        order = Order.objects.create(
            kind_id=data['kind'],
            quality=Quality.objects.get(primary=True),
            rule=';'.join([f'{part_name}:{finish}' for part_name, finish in data['parts'].items()]),
            running=False
        )

        cache.set(RENDER_ORDER_KEY.format(order.id), self.channel_name, 600)
        cache.set(CURRENT_ORDER_KEY.format(self.channel_name), order.id, 600)

        return order.id

    @database_sync_to_async
    def check_if_render_exists(self, product_kind_id, parts):
        kind = ProductKind.objects.get(id=product_kind_id)
        filename = kind.parse_rules([f'{part}:{finish}' for part, finish in parts.items()], only_one=True)

        if 'file' not in filename:
            print(filename)
            return False, None

        quality = Quality.objects.get(primary=True)
        path = os.path.join(str(kind.product.id), str(quality.id), f'{filename["file"]}.jpg')
        return os.path.exists(os.path.join(settings.MEDIA_ROOT, path)), path

    async def receive_json(self, data, **kwargs):
        if data['type'] == 'get_render':
            cache.delete(RENDER_ORDER_KEY.format(cache.get(CURRENT_ORDER_KEY.format(self.channel_name))))

            exists, path = await self.check_if_render_exists(data['kind'], data['parts'])
            if exists:
                await self.send_json({
                    'type': 'render_created',
                    'event': {'render_path': settings.MEDIA_URL + path}
                })
            else:
                await self.create_order(data)


