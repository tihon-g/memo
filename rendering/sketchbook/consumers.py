import os

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from furniture.models import ProductKind
from render.models import Order, Quality
from django.core.cache import cache

from sketchbook.exceptions import ParseRulesError

RENDER_ORDER_KEY = 'sketchbook_render_order_id_{}'
CURRENT_ORDER_KEY = 'sketchbook_current_order_{}'


def notify_render_created(path, order_id):
    channel_layer = get_channel_layer()

    message = {'type': 'render_created', 'render_path': path, 'order_id': order_id}
    channel_name = cache.get(RENDER_ORDER_KEY.format(order_id))
    if channel_name:
        async_to_sync(channel_layer.send)(channel_name, message)


def notify_render_error(order_id, exception_text):
    channel_layer = get_channel_layer()

    message = {'type': 'render_error', 'text': exception_text, 'order_id': order_id}
    channel_name = cache.get(RENDER_ORDER_KEY.format(order_id))
    if channel_name:
        async_to_sync(channel_layer.send)(channel_name, message)


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

    async def receive_json(self, data, **kwargs):
        if data['type'] == 'get_render':
            await self.get_render(data)

    async def get_render(self, data):
        self.clear_current_client_order()

        rules = [f'{part}:{finish}' for part, finish in data['parts'].items()]

        try:
            filename = await self.parse_rules(data['kind'], rules)
        except ParseRulesError as e:
            await self.channel_layer.send(self.channel_name, {'type': 'render_error', 'text': repr(e)})
            return

        exists, path = await self.check_if_render_exists(data['kind'], filename)

        if exists:
            await self.send_json({
                'type': 'render_created',
                'event': {'render_path': settings.MEDIA_URL + path}
            })
        else:
            await self.create_order(data, rules)

    @database_sync_to_async
    def create_order(self, data, rules):
        order = Order.objects.create(
            kind_id=data['kind'],
            quality=Quality.objects.get(primary=True),
            rule=';'.join(rules),
            running=False
        )

        self.set_current_client_order(order.id)

        return order.id

    @database_sync_to_async
    def parse_rules(self, product_kind_id, rules):
        kind = ProductKind.objects.get(id=product_kind_id)
        filename = kind.parse_rules(rules, only_one=True)

        if 'error' in filename:
            raise ParseRulesError(filename['error'])

        return filename['file']

    @database_sync_to_async
    def check_if_render_exists(self, product_kind_id, filename):
        kind = ProductKind.objects.get(id=product_kind_id)
        quality = Quality.objects.get(primary=True)

        path = os.path.join(str(kind.product.id), str(quality.id), f'{filename}.{quality.ext}')
        return os.path.exists(os.path.join(settings.MEDIA_ROOT, path)), path

    def clear_current_client_order(self):
        cache.delete(RENDER_ORDER_KEY.format(cache.get(CURRENT_ORDER_KEY.format(self.channel_name))))

    def set_current_client_order(self, order_id):
        cache.set(RENDER_ORDER_KEY.format(order_id), self.channel_name, 600)
        cache.set(CURRENT_ORDER_KEY.format(self.channel_name), order_id, 600)
