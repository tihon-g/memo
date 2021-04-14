# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from render.models import Order, Machine
#from render.utils import execute_wait
import psutil
from time import sleep
from django.core.management import call_command
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Manage queue and run blender then need'

    def handle(self, *args, **options):
        if not os.getenv('BLENDER_LOCAL'):
            print("specify ENV: 'BLENDER_LOCAL'. I don't know witch blender you want to use and where is it configured")
            return
        # #it can be rewrite os environ from another location
        load_dotenv(dotenv_path=os.getenv('BLENDER_LOCAL'), verbose=True)
        if not os.getenv('BLENDER'):
            print("specify 'BLENDER' in enviro. I don't know witch blender you want to use and where is it configured")
            return
        print(f'Start processing_orders_server...')
        w = Machine.objects.get(name=os.getenv('RENDER_MACHINE'))
        while True:
            try:
                queue1 = Order.objects.filter(running=False).filter(worker=w)
                queue2 = Order.objects.filter(running=False).filter(worker__isnull=True)
                if not queue1 and not queue2:
                    sleep(3)
                    continue
                print(f'processing_orders_server')
                for p in psutil.process_iter():
                    if os.path.basename(os.getenv('BLENDER')) == p.name():
                        sleep(3)
                        break
                else:  # no any blender processes
                    if queue1:
                        call_command('blender', queue1.first().id)
                    else:
                        call_command('blender', queue2.first().id)
                sleep(3)
            except:
                pass
        print(f'end processing_orders_server...')
