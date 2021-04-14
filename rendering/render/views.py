# import asyncio
import subprocess
import psutil
import json
import os
#import psutil
import time
# from pathlib import Path
from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from furniture.models import Model3D, ProductKind, Product, Configuration
from material.models import Finish
from wcmatch import pathlib

from .models import Order, Scene, Actor, Camera, Quality, Machine
from render.utils import execute_wait
# for top part of page about server

# def server_view(request):
#     if request.method == 'POST':
#         if 'kill_processes' in request.POST:
#             killAllRenderers(request)
#
#         # if 'start_process' in request.POST:
#         #     startProc()
#         #     messages.add_message(request, messages.INFO, 'Run rendering!')
#
#         if 'kill_queue_manager' in request.POST:
#             killQueueManager(request)
#
#         if 'start_queue_manager' in request.POST:
#             call_command('queue')
#             messages.add_message(request, messages.INFO, 'Run Queue Manager!')

def procList(procname):
    procs = []
    for p in psutil.process_iter():
        try:
            if procname == p.name() and p.is_running() and p.cmdline():
                procs.append(p)
        except:
            pass
    return procs

def get_server_info():
    blender = {}
    redis = {'config': settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'], "status": 'not active'}
    rabbit = {'config': os.getenv('RABBIT_HOST')}
    python = []

    for p in procList('Python'):
        if 'queue' in p.cmdline():
            python.append(p)
    # https://psutil.readthedocs.io/en/latest/index.html?highlight=on%20terminate#psutil.Process.terminate
    memory = {}  # psutil.memory_info()

    # check redis (for Websockets)
    for s in execute_wait(['redis-cli', 'ping']):
        if 'PONG' in s:
            redis["status"] = 'active'
            break

    if os.getenv('BLENDER_LOCAL'):
        from dotenv import load_dotenv
        # it can be rewrite os environ from another location
        load_dotenv(dotenv_path=os.getenv('BLENDER_LOCAL'), verbose=True)
        blender['machine'] = os.getenv('RENDER_MACHINE')
        blender['version'] = os.getenv('BLENDER_VERSION')
        blender['processes'] = procList(os.path.basename(os.getenv('BLENDER')))

    db_engine = settings.DATABASES['default']['ENGINE'].split('.')[-1]
    db_host = 'local'
    if 'sqlite' not in db_engine:
        db_host = settings.DATABASES['default']['HOST']
    return {
        "db": {
            "engine": f"{db_engine} @ {db_host} ",
            "models": Model3D.objects.filter(blend__isnull=False),
            "kinds": ProductKind.objects.filter(product__model__blend__isnull=False),
            "orders": {
                "in_queue": Order.objects.filter(running__isnull=False),  # "#n: volume"
                "from_API": "",
                "from_scketchbook": ""
            }
        },
        'queue': {
            "manager": "",
            "orders": ""
        },
        'redis': redis,
        'blender': blender,
        'rabbit': rabbit,
        'python': python,
        "machines": Machine.objects.all()
    }

def kill_blender(request, pids = "-"):
    try:
        if pids and pids != '-':
            for pid in pids.split('-'):
                p = psutil.Process(int(pid))
                if p.name() == os.path.basename(os.getenv('BLENDER')):
                    en = p.environ()
                    if 'RENDER_ORDER_ID' in en:
                        p.terminate()
                        p.wait()
                        o = Order.objects.get(pk=int(en['RENDER_ORDER_ID']))
                        o.cancel()
                        messages.add_message(request, messages.WARNING, f'{p} terminated')
        else:
            # find all blender processes and kill that
            pass
    except Exception as err:
        print(repr(err))
        return redirect('render:index')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def killQueueManager(request, pids = ""):
    try:
        if pids:
            for pid in pids.split('-'):
                p = psutil.Process(int(pid))
                cmd = p.cmdline()
                if p.name() == 'Python' and 'queue' in cmd and 'manage.py' in cmd:
                    p.terminate()
                    p.wait()
    except Exception as err:
        print(repr(err))
        return redirect('render:index')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def startQueueManager(request):
    subprocess.Popen([os.getenv('PYTHON'), "manage.py", "queue"], cwd=settings.BASE_DIR)
    #call_command('queue')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# todo: asinc тут само то сделать!!
def index(request):  # async
    #context = {}
    #server_view(request)

    return render(request, 'render/index.html',
        {
        'products': Product.objects.filter(model__blend__isnull=False),  # Products with blend files inside
        'server': get_server_info(),
        'nav_active': 'render',
        })


def add_model_to_scene(n, model_id, post):
    meshes = {}
    # get meshes & finishes
    a = Actor()
    a.model_id = model_id
    # get object position & rotation
    a.set_position([float(post[f'{c}-{n}']) for c in ['pos-x', 'pos-y', 'rot-z']])

    for k, v in post.items():
        if f'mesh-show-{n}-' in k:
            mesh = k.split('-')[-1]
            finish_id = int(post[f'finish-{n}-{mesh}'])
            if finish_id:
                meshes[mesh] = finish_id
    a.finishesOnMeshes = json.dumps(meshes, indent=2)
    print('add_model_to_scene', model_id, a.finishesOnMeshes)
    return a


def scene_details(request, scene_id):
    context = {
        'scene': Scene.objects.get(pk=scene_id)
    }
    return render(request, 'scene-details.html', context)

def scene(request):
    context = {
        'models': Model3D.objects.filter(glb__isnull=False).filter(blend__isnull=False),
        #'meshes': Mesh.objects.filter(model__glb__isnull=False),
        'finishes': Finish.objects.exclude(name__isnull=True).exclude(archive=1),
        'hdrmaps': [os.path.basename(f) for f in
                    pathlib.Path(os.path.join(settings.STATIC_ROOT, 'furniture', 'models', 'hdri')).glob("*.hdr")],
        # todo from db
        'data': {},
        'actors': []
    }

    if request.method == 'POST':
        #if "scene-render" in request.POST:
        scene = Scene()
        # scene = Scene.objects.get(pk=1)
        scene.name = 'scene ' + str(datetime.now())
        #world = models.FileField(null=True)
        scene.quality = Quality.objects.get(pk=1)
        # get camera position & lookAt direction
        camera = Camera()
        # camera = Camera.objects.get(pk=1)
        camera.set_angles([float(x) for x in request.POST['camera-pos'].split('|')])
        camera.set_lookAt([float(x) for x in request.POST['camera-lookAt'].split('|')])
        camera.focus = 40 #  int(request.POST['camera-fov'])
        #fov (vert) = 40, tan20=0.36, height sensor 36, height 36 => focus = 50
        camera.save()
        scene.camera = camera
        scene.save()
        for k, v in request.POST.items():
            if 'model-show-' in k:
                n, model_id = k[len('model-show-'):].split('-')
                a = add_model_to_scene(int(n), int(model_id), request.POST)
                a.scene = scene
                a.save()
                context['actors'].append(a)
        return redirect('render:scene-details', scene_id=scene.id)
        messages.add_message(request, messages.INFO, f"Let's start rendering scene...with {len(Actor.objects.filter(scene=scene))} models, look in status bar for progress ")
        # data = .. to do pass back data from POST to form

    return render(request, 'scene.html', context)  # todo put in context camera position. and other data

@staff_member_required
def productOrders(request, product_id):
    #server_view(request)
    if request.method == 'POST':
        if 'product-select' in request.POST:
            return redirect('render:product-orders', int(request.POST['product-select']))
        if 'order-new' in request.POST:
            rule = request.POST['rule']
            kind_id = int(request.POST['kind'])
            quality_id = int(request.POST['quality'])
            try:
                kind = ProductKind.objects.get(pk=kind_id)
                parsed = kind.parse_rules(rule.split(';'))
                if 'error' in parsed:
                    messages.add_message(request, messages.ERROR, f"{parsed['error']}")
                else:
                    order = Order()
                    order.kind_id = kind_id
                    order.rule = rule
                    order.quality_id = quality_id
                    order.save()
                    messages.add_message(request, messages.INFO, f'{order} created!')
            except Exception as e:
                messages.add_message(request, messages.ERROR, repr(e))

    return render(request, 'render/product_orders.html',
                  {'product': Product.objects.get(pk=product_id),
                   'qualities': Quality.objects.all(),
                   #'products': Product.objects.filter(model__blend__isnull=False),
                   'orders': Order.objects.filter(kind__product_id=product_id),
                   'server': get_server_info(),
                  })


def orderSketchbook(request, pk):
    order = Order.objects.get(pk=pk)
    product = order.kind.product
    parts = Configuration.objects.filter(kind=order.kind).prefetch_related()

    context = {
        'order': order,
        'finishes': order.kind.usedFinishes,
        'parts': parts,
    }
    return render(request, 'render/orderSketchbook.html', context)


def productSketchbook(request, product_id):
    product = Product.objects.get(pk=product_id)
    kinds = ProductKind.objects.filter(product_id=product_id).order_by('id')
    kindParts = {}
    for k in kinds:
        kindParts[k.id] = Configuration.objects.filter(kind_id=k.id).prefetch_related() #depth=2
    context = {
        'product': product,
        #'orders': Order.objects.filter(kind__product_id=product_id).order_by('id'),
        'finishes': product.usedFinishes,
        'kind_parts': kindParts,
    }
    return render(request, 'render/productSketchbook.html', context)


def orderRun(request, pk):
    try:
        o = Order.objects.get(pk=pk)
        # if o.worker:
        #     if o.worker.name != settings.RENDER_MACHINE['NAME']:
        #         messages.add_message(request, messages.ERROR, "Another worker doing this order")
        #         return
        # else:
        #     o.worker = Machine.objects.get(name=settings.RENDER_MACHINE['NAME'])
        #     o.save()
        res = o.run()
        # from django.core.management import call_command
        # res = call_command('blender', pk)
        #messages.add_message(request, messages.INFO, res)

        # if res == 'ok':
        #     messages.add_message(request, messages.INFO, 'Order put in the queue and successfully arranged in rabbitMQ')
        # else:
        #     messages.add_message(request, messages.ERROR, res)
    except Exception as err:
        messages.add_message(request, messages.ERROR, repr(err))
    return redirect('render:product-orders', o.kind.product.id)


def orderCancel(request, pk):
    o = Order.objects.get(pk=pk)
    o.cancel()
    return redirect('render:product-orders', o.kind.product.id)


def orderStop(request, pk):
    o = Order.objects.get(pk=pk)
    try:
        os.remove(os.path.join(o.rendersPath, 'stopfile'))
        # to do rabbit
        if o.worker.name == os.getenv('RENDER_MACHINE'):
            pass
            # wait for blender quits? or quit?
    except Exception as e:
        print(e)
    #return redirect('render:product-orders', o.kind.product.id)
    return orderCancel(request, pk)


@staff_member_required
def post_order_data(request, pk, copy_type):  # copy/move/sym
    order = Order.objects.get(pk=pk)
    try:
        order.postData(copy_type)
        messages.add_message(request, messages.INFO, f"Render images posted to quality folder '{order.quality.id}':  {order.quality}")
    except Exception as err:
        messages.add_message(request, messages.ERROR, repr(err))
    return redirect('render:product-orders', order.kind.product.id)

@staff_member_required
def remove_order_data(request, pk):
    order = Order.objects.get(pk=pk)
    try:
        order.cleanData()
    except Exception as err:
        messages.add_message(request, messages.ERROR, repr(err))
    return redirect('render:product-orders', order.kind.product.id)


def orderDelete(request, pk):
    order = Order.objects.get(pk=pk)
    product_id = order.kind.product.id
    messages.add_message(request, messages.INFO, f"{order} deleted")
    order.delete()
    return redirect('render:product-orders', product_id)


def activity_scene(request, scene_id):
    percent = 0
    try:
        with open(os.path.join(settings.MEDIA_ROOT, 'scenes', f'{scene_id}.state'), 'r') as state:
            percent = int(state.read().split(' ')[-1])
    except:
        pass
    return JsonResponse({
                         'percent': percent,
                         })

def ajax_orderqueue(request):
    orders = Order.objects.exclude(running__isnull=True)
    result = {}
    for order in orders:
        result[order.id] = {'kind': order.kind.name,
                            'product_ref': reverse("render:product-orders", args=[order.kind.product_id]),
                            'running': order.running,
                            'worker': order.worker.name if order.worker else "",
                            'N': order.N,
                            'done': order.renders_done}
    return JsonResponse(result, status=200)

# def ajax_activity(request):
#     samples = [0, 1]
#     done = 0
#     try:
#         orders = Order.objects.filter(running=True)
#         result = {}
#         for order in orders:
#             result[order.id] = {'done': order.renders_done}
#             if settings.RENDER_MACHINE['NAME'] == order.worker.name: #
#                 with open(os.path.join(order.get_renders_dir(), 'state'), 'r') as state:
#                     samples = state.readlines()[-1].rstrip('\n').split(' ')
#                     result[order.id]['cur_sample'] = samples[0]
#                     result[order.id]['samples'] = samples[1]
#     except:
#         pass
#     return JsonResponse(result, status=200)


def ajaxCreateOrder(request):
    try:
        if request.method == 'POST':
            order = Order()
            order.created_by = request.user
            data = json.loads(request.body)
            order.kind_id = data['kind']
            order.quality_id = settings.RENDER_MACHINE['QUALITY']
            order.rule = data['rule']
            order.running = False
            order.save()
            return JsonResponse({'order': order.pk}, status=200)
        return JsonResponse({'error': 'wrong method'}, status=400)
    except Exception as err:
        return JsonResponse({'error': str(err)}, status=500)


def ajax_order_status(request, pk):
    order = Order.objects.get(pk=pk)
    result = {'kind': order.kind.name,
            'running': order.running,
            'worker': order.worker.name if order.worker else "",
            'N': order.volume,
            'done': order.renders_done,
            #'url': order.url()
            }
    return JsonResponse(result)


def ajax_get_all_product_renders(request, product_id):
    return JsonResponse({'renders': Product.objects.get(pk=product_id).renders})


def ajax_get_all_order_renders(request, pk):
    return JsonResponse({'renders': Order.objects.get(pk=pk).renders})
