from django.core.management.base import BaseCommand
import os

from render.models import Order
import requests
from wcmatch import pathlib

url_post ="http://renders.memofurniture.com/v2/render_upload?memo_pn={}&config={}"

class Command(BaseCommand):
    help = 'post renders'

    def add_arguments(self, parser):
        parser.add_argument('order', nargs=1, type=int, default=False)

    def handle(self, *args, **options):
        print("Start posting to cloud script...\n")
        try:
            order = Order.objects.get(pk=options['order'][0])
        except Exception as e:
            print('bad parameter to do post renders: {}'.format(options['order'][0]))
            exit()
        q = order.quality
        root = pathlib.Path(os.path.join(order.rendersPath, str(q.id)))
        for f in root.glob(f"*.{q.ext}"):
            pairs = os.path.basename(f).split('.')[0].split("=")[1].split('_')
            meshes = {}
            conf = []
            for pair in pairs:
                mesh, mat = pair.split("-")
                meshes[mesh] = mat
            for part in order.kind.parts.all():
                p = part.name.lower()
                # bad conf for do  - for lastaR (((
                if p == 'bolsters':
                    p = 'back'
                if p == 'pads':
                    p = 'seat'
                conf.append(f"{p}:{meshes[part.meshes.all()[0].name]}")
            print(conf, end='...')

            if 200 == requests.post(url_post.format(order.kind.product.id, '-'.join(conf)), files={'file': open(f, 'rb')}).status_code:
               print('OK')
            else:
               print("failed")
