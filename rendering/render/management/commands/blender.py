# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from render.models import Order, Machine
from render.utils import execute_wait
from dotenv import load_dotenv

# another way
# import djclick as click
#
# @click.command()
# @click.argument('name')
# def command(name):
#     click.secho('Hello, {}'.format(name), fg='red')

class Command(BaseCommand):
    help = 'Manage queue and run blender then need'
    state = {}
    o = None
    def add_arguments(self, parser):
        parser.add_argument('order_id', nargs='?', type=int, default=False)

    def handle(self, *args, **options):
        # check configuration
        if not os.getenv('BLENDER'):
            if os.getenv('BLENDER_LOCAL'):
                load_dotenv(dotenv_path=os.getenv('BLENDER_LOCAL'), verbose=True)
                if not os.getenv('BLENDER'):
                    print(f"specify properly 'BLENDER' env in {os.getenv('BLENDER_LOCAL')}. I don't know witch blender you want to use and where is it configured")
                    return
            else:
                print("specify ENV: 'BLENDER_LOCAL'. I don't know witch blender you want to use and where is it configured")
                return
        # one more check (config)
        if not os.getenv('RENDER_MACHINE') or not os.getenv('BLENDER_PY'):
            print("specify ENV: 'RENDER_MACHINE' & 'BLENDER & BLENDER_PY' on this machine! Can't run rendering process!")
            return
        # check installation
        if not os.path.exists(os.environ.get("BLENDER")):
            print(f"There is no blender installed - {os.environ.get('BLENDER')}")
            return
        if not os.path.exists(os.environ.get("BLENDER_PY")):
            print(f"There is no blender script located - {os.environ.get('BLENDER_PY')}")
            return
        machine = None
        order_id = None
        try:
            order_id = options['order_id']
        except:
            print("use 'python manage.py blender <order_id>'")
            for o in Order.objects.all():
                print(o)
            return
        try:
            machine = Machine.objects.get(name=os.getenv('RENDER_MACHINE'))
        except:
            machine = Machine()
            machine.name = os.getenv('RENDER_MACHINE')
            machine.save()
        # find
        try:
            # there is no our running  order - get one from queue
            o = Order.objects.get(pk=order_id)
            model3d = os.path.join(settings.BASE_DIR, str(o.kind.product.model.blend).replace('/', os.sep))
            cmd = [os.getenv('BLENDER'), model3d, '--background', '-noaudio', '--python', os.getenv('BLENDER_PY')]
            os.environ['RENDER_ORDER_ID'] = str(o.id)
            print(f"start rendering order {o}, cmd={cmd}")
            last = ""
            for s in execute_wait(cmd):
                if settings.DEBUG:
                    print(s)

        except ValueError as e:
            print(f"errror: there is no model file for running order. Remove it from queue. {repr(e)} ")
            #o.cancel()
        except Exception as e:
            print(f"error: exception: {repr(e)}")
            #o.cancel()

