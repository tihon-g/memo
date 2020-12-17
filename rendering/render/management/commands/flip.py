from django.core.management.base import BaseCommand
import os

from render.models import Order
import requests
from wcmatch import pathlib
from PIL import Image

class Command(BaseCommand):
    help = 'post renders'

    def add_arguments(self, parser):
        parser.add_argument('order', nargs=1, type=int, default=False)

    def handle(self, *args, **options):
        print("Start flip images...\n")
        try:
            order = Order.objects.get(pk=options['order'][0])
        except Exception as e:
            print('bad parameter to do post renders: {}'.format(options['order'][0]))
            exit()
        q = order.quality
        root = pathlib.Path(os.path.join(order.rendersPath, str(q.id)))
        for f in root.glob(f"*.{q.ext}"):
            # read the image
            im = Image.open(f)
            # flip image
            print(f, end='...')
            out = im.transpose(Image.FLIP_LEFT_RIGHT)
            out.save(f)
            print('OK')

