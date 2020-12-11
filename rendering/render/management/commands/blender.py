# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from render.models import Order, Machine, execute_wait


class Command(BaseCommand):
    help = 'Manage queue and run blender then need'
    state = {}
    o = None
    def add_arguments(self, parser):
        parser.add_argument('order_id', nargs='?', type=int, default=False)

    def handle(self, *args, **options):
        if not os.getenv('BLENDER_LOCAL'):
            print("specify ENV: 'BLENDER_LOCAL'. I don't know witch blender you want to use and where is it configured")
            return
        from dotenv import load_dotenv
        #it can be rewrite os environ from another location
        load_dotenv(dotenv_path=os.getenv('BLENDER_LOCAL'), verbose=True)

        if not os.getenv('RENDER_MACHINE') or not os.getenv('BLENDER') or not os.getenv('BLENDER_PY'):
            print("specify ENV: 'RENDER_MACHINE' & 'BLENDER & BLENDER_PY' on this machine! Can't run rendering process!")
            return
        if not os.path.exists(os.environ.get("BLENDER")):
            print(f"There is no blender installed - {os.environ.get('BLENDER')}")
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
            print(f"start rendering order {o}")
            model3d = os.path.join(settings.BASE_DIR, str(o.kind.product.model.blend).replace('/', os.sep))
            cmd = [os.getenv('BLENDER'), model3d, '--background', '-noaudio', '--python', os.getenv('BLENDER_PY')]
            print(f"** call blender for {o} **")
            os.environ['RENDER_ORDER_ID'] = str(o.id)
            last = ""
            for s in execute_wait(cmd):
                print(s)


        except ValueError as e:
            print(f"errror: there is no model file for running order. Remove it from queue. {repr(e)} ")
            #o.cancel()
        except Exception as e:
            print(f"error: exception: {repr(e)}")
            #o.cancel()


    # def parsing(self, s, order):
    #     # if s.startswith('Saved:'):
    #     #     print(f"blender.py ---> new one: {s}")
    #     #     with open(os.path.join(order.rendersPath, 'state'), 'w') as state:
    #     #         state.write('')
    #     # elif s.endswith('samples'):
    #     #     with open(os.path.join(order.rendersPath, 'state'), 'a') as state:
    #     #         state.write((' '.join(s.split('|')[-1].split(' ')[2:5:2]))+'\n')
    #     #         print(f"blender.py-> {s}", end='\n')
    #     # elif 'STOP' in s or 'exception' in s:  #exit by deleteing stopfile
    #     #     order.running = None  # if stopfile was deleted outside django
    #     #     order.save()
    #     #     print(f"STOP {s}")
    #     # else:
    #     #print(f"blender.py-> {s}", end='\n')
    #     if s.startswith('!!'):
    #         print(s[2:])
