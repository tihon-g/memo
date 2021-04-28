import os

from django.core.management import call_command
from dotenv import load_dotenv

from render.models import Machine
from rendering.celery import app


@app.task
def process_order_render(order_id, worker_id):
    if not os.getenv('BLENDER_LOCAL'):
        print("specify ENV: 'BLENDER_LOCAL'. I don't know witch blender you want to use and where is it configured")
        return
    # #it can be rewrite os environ from another location
    load_dotenv(dotenv_path=os.getenv('BLENDER_LOCAL'), verbose=True)
    if not os.getenv('BLENDER'):
        print("specify 'BLENDER' in enviro. I don't know witch blender you want to use and where is it configured")
        return
    print(f'Start processing_orders_server...')

    worker = Machine.objects.get(name=os.getenv('RENDER_MACHINE'))

    if not worker_id or worker_id == worker.id:
        call_command('blender', order_id)
