# -*- coding: utf-8 -*-
# read RENDER_ORDER_ID from environ
# read all data from django using DJANGO_SETTINGS_MODULE

import bpy  # blender python - can run only from blender(
from datetime import datetime
import os, sys

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

start = datetime.now()

bl_version = bpy.app.version_string.split(' ')[0]
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

BASE_DIR = os.getenv('DJANGO_BASE_DIR')  # it was set after settings imports??
print(f'>>blender.py, based={BASE_DIR} python={py_version}, blender={bl_version}')

if sys.platform == 'darwin':
    sys.path.append(f'/Applications/Blender.app/Contents/Resources/{bl_version}/python/lib/python{py_version}/site-packages')

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import django
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rendering.settings")
django.setup()

from django.conf import settings
from furniture.models import Product, Model3D, Configuration
from render.models import Order, Machine#, Shot

F_DIR = os.path.join(settings.STATIC_ROOT, 'material', 'finishes').replace("/", os.sep)
scene = bpy.data.scenes[0]

blend = bpy.context.blend_data.filepath  # os.path.basename
model = Model3D.objects.get(blend=os.path.relpath(blend, BASE_DIR).replace(os.sep, '/'))
# todo check name in blend field with or no static/furniture/...

worker = Machine.objects.get(name=os.getenv('RENDER_MACHINE')) # settings.RENDER_MACHINE['NAME'])
order_id = os.environ.get('RENDER_ORDER_ID')
try:
    order = Order.objects.get(pk=int(order_id))
except Exception as e:
    print(f"exception order id: {repr(e)}")
    exit()
# orders = Order.objects.filter(kind__product__model_id=model.id).filter(running=1).filter(worker=worker)
# if len(orders):
#     order = orders.first()
# else:
#     print(f"No any orders for {model.name} with running==1 for this render machine")
#     exit()
stop_file = os.path.join(order.rendersPath, 'stopfile')
current_job = {}
cycles = order.cycles
worker.activeOrder = order
worker.save()
order.running = True
order.worker = worker
print(f'!! set worker:${worker}')
if order.volume != order.N:
    order.volume = order.N
if not order.rule:
    order.rule = order.kind.renderOrderTemplate.replace('{}', '*').replace('-',';')
order.save()
dest_folder = ""
relPath = ""


def do_rendering(deep, prev_cover):
    """
    main recursive function for rendering witch change material for a while
    :param deep: deep of reccursion
    :param cover: string presented witch materials were set berore
    :return:
    """
    cycle = cycles[deep]

    print(f"do_rendering {deep}|{prev_cover}")
    finishes = cycle['finishes']
    if cycle['config'].colorChart:
        prev = prev_cover.split('_')[-1]
        finishes = cycle['config'].colorChart.match(prev) # only one, but maybe array
    pat = -1
    for f in finishes:
        if f.pattern.id != pat:
            apply_patttern(deep, f.pattern)
            pat = f.pattern.id
        apply_mat(deep, f)
        cover = prev_cover + '_' + str(f.id if f.pattern.nature.name != 'none' else 0)
        if deep+1 < len(cycles):
            do_rendering(deep+1, cover)
        else:
            if order.volume>1:
                if not os.path.exists(stop_file):
                    #order.cancel()
                    print(f"!!STOP!! stop_file deleted!! we must stop now. {current_job['counter']} renders added on this round")
                    exit()  # only one legal exit
            do_and_save_render(cover)
        print(f"** end pattern {pat} **")
    print(f"** end do_rendering {deep} {prev_cover} **")

# todo check different shader for different cycles
def set_same_shader_for_all_meshes_in_cycle(meshes): # names in array
    mat = scene.objects[meshes[0]].data.materials[0]
    for k in range(1, len(meshes)):
        scene.objects[meshes[k]].data.materials[0] = mat

def apply_patttern(deep, p):
    try:
        if p.nature.name == 'none':
            return
        material = materials[deep]
        print(f"apply pattern id:{p.id} mat={material.name}")
        shader = material.node_tree
        if p.diffuse and 'diffuse' in shader.nodes:
            # load image
            if p.diffuse not in bpy.data.images:
                bpy.ops.image.open(filepath=os.path.join(F_DIR, str(p.pk), p.diffuse))
                bpy.data.images[p.diffuse].source = 'FILE'
                print(f"loaded {p.diffuse} image!")
            # set image
            shader.nodes['diffuse'].image = bpy.data.images[p.diffuse]
            shader.nodes['diffuse'].image.colorspace_settings.name = 'sRGB'
        if p.roughness and 'roughness' in shader.nodes:
            # load image
            if p.roughness not in bpy.data.images:
                bpy.ops.image.open(filepath=os.path.join(F_DIR, str(p.pk), p.roughness))
                bpy.data.images[p.roughness].source = 'FILE'
                print(f"loaded {p.roughness} image!")
            # set image
            shader.nodes['roughness'].image = bpy.data.images[p.roughness]
            shader.nodes['roughness'].image.colorspace_settings.name = 'Linear'
        if p.normal and 'normal' in shader.nodes:
            # load image
            if p.normal not in bpy.data.images:
                bpy.ops.image.open(filepath=os.path.join(F_DIR, str(p.pk), p.normal))
                bpy.data.images[p.normal].source = 'FILE'
                print(f"loaded {p.normal} image!")
            # set image
            shader.nodes["Normal Map"].inputs[0].default_value = 1
            shader.nodes['normal'].image = bpy.data.images[p.normal]
            shader.nodes['normal'].image.colorspace_settings.name = 'Linear'
        if p.tile:
            if p.tile.multiplier:  # scale
                for k in range(3):
                    shader.nodes['Mapping'].inputs[3].default_value[k] = p.tile.multiplier

        shader.nodes["Hue Saturation Value"].inputs[0].default_value = 0.5
        shader.nodes["Hue Saturation Value"].inputs[1].default_value = 1
        shader.nodes["Hue Saturation Value"].inputs[2].default_value = 1

        if p.features:
            if p.features.diffuse_hsv:
                shader.nodes["Hue Saturation Value"].inputs[0].default_value = p.features.diffuse_hsv.hue
                shader.nodes["Hue Saturation Value"].inputs[1].default_value = p.features.diffuse_hsv.saturation
                shader.nodes["Hue Saturation Value"].inputs[2].default_value = p.features.diffuse_hsv.value
    except Exception as e:
        print(f"!!Exception {repr(e)}")
        order.running = None
        order.save()
        return

def apply_mat(deep, m):
    print(f"apply_mat on {cycles[deep]['meshes']}, finish id: {m.id}")
    shader = materials[deep].node_tree
    if m.pattern.nature.name == 'none':
        for mesh in cycles[deep]['meshes']:
            scene.objects[mesh].hide_render = True
        print(f"hide {cycles[deep]['meshes']}")
        return

    for mesh in cycles[deep]['meshes']:
        scene.objects[mesh].hide_render = False

    if 'diffuse' in shader.nodes:
        if m.diffuse:
            # load image
            if m.diffuse not in bpy.data.images:
                bpy.ops.image.open(filepath=os.path.join(F_DIR, str(m.pattern_id), m.diffuse))
                bpy.data.images[m.diffuse].source = 'FILE'
                print(f"diffuse - loaded {m.diffuse} image!")
            # set image
            shader.nodes['diffuse'].image = bpy.data.images[m.diffuse]
            shader.nodes['diffuse'].image.colorspace_settings.name = 'sRGB'
        else:
            shader.nodes['diffuse'].image = None
    else:
        # todo use features.color?
        pass
    if 'roughness' in shader.nodes:
        if m.roughness:
          # load image
            if m.roughness not in bpy.data.images:
                bpy.ops.image.open(filepath=os.path.join(F_DIR, str(m.pattern_id), m.roughness))
                bpy.data.images[m.roughness].source = 'FILE'
                print(f"roughness - loaded {m.roughness} image!")
            # set image
            shader.nodes['roughness'].image = bpy.data.images[m.roughness]
            shader.nodes['roughness'].image.colorspace_settings.name = 'Linear'
        else:
            shader.nodes['roughness'].image = None
    else:
        # todo use features.roughness?
        pass
    if 'normal' in shader.nodes:
        if m.normal:
            if m.normal not in bpy.data.images: # load image
                bpy.ops.image.open(filepath=os.path.join(F_DIR, str(m.pattern_id), m.normal))
                bpy.data.images[m.normal].source = 'FILE'
                print(f"normal - loaded {m.normal} image!")
            # set image
            shader.nodes["Normal Map"].inputs[0].default_value = 1
            shader.nodes['normal'].image = bpy.data.images[m.normal]
            shader.nodes['normal'].image.colorspace_settings.name = 'Linear'
        else:
            shader.nodes['normal'].image = None
    else:
        # todo use features.normal?
        pass
    if m.features:
        if m.features.diffuse_hsv:
            shader.nodes["Hue Saturation Value"].inputs[0].default_value = m.features.diffuse_hsv.hue
            shader.nodes["Hue Saturation Value"].inputs[1].default_value = m.features.diffuse_hsv.saturation
            shader.nodes["Hue Saturation Value"].inputs[2].default_value = m.features.diffuse_hsv.value


def notify_render_created(path, order):
    channel_layer = get_channel_layer()

    message = {'type': 'render_created', 'render_path': path, 'order_id': order.id}
    async_to_sync(channel_layer.group_send)('sketchbook', message)


def do_and_save_render(cover, shadow=False):
    if cover in current_job['done_renders']:
        print(f'already done {cover}')
        return
    f = order.kind.filename(cover[1:].split('_')) + f'.{order.quality.ext}'
    fullpath = os.path.join(dest_folder, f)
    print(f'!!start make and save render [{cover}] in {fullpath}')
    scene.render.filepath = fullpath
    started = datetime.now()
    bpy.ops.render.render(write_still=True)
    if order.running:
        if order.volume > 1:
            current_job['counter'] += 1
            with open(order.doneLog['url'], 'a') as data_renders_log:
                data_renders_log.write(cover + '\n')
            current_job['done_renders'].append(cover)
        difference = datetime.now() - started
        worker.render_made()
        order.renders_done += 1
        order.save()

        path = os.path.join(relPath, f)
        notify_render_created(settings.MEDIA_URL + path, order)

        print(f'!!saved|{order.renders_done}|{path}|{difference}')
    else:
        print("!!EXIT!! someone stop order. exit!")
        exit()

if __name__ == "__main__":
    # hide not covered meshes
    for mesh in order.kind.product.model.meshes:
        if order.kind.deep(mesh.name) < 0:
            print(f'{mesh.name} will be hidden')
            scene.objects[mesh.name].hide_render = True
    materials = []  # array for material on every deep level
    for cycle in order.cycles:
        if len(cycle['meshes']) > 1:
            set_same_shader_for_all_meshes_in_cycle(cycle['meshes'])
        materials.append(scene.objects[cycle['meshes'][0]].data.materials[0])

    if order.volume > 1:
        # manage big orders
        relPath = os.path.join(order.relRendersPath, str(order.quality.id))
    else:
        relPath = os.path.join(order.kind.product.relRendersPath, str(order.quality.id))  # direct in MEDIA_ROOT
    dest_folder = os.path.join(os.getenv('RENDER_DIR'), relPath)
    try:
        os.makedirs(dest_folder)
    except:
        pass
    if order.volume > 1:
        done = []  # list of ready renders for this order.
        if not os.path.exists(order.doneLog['url']):  # start order from the begining
            with open(order.doneLog['url'], 'w') as data_renders_log:  # save output directory & render options
                data_renders_log.write('\t'.join([datetime.now().strftime("%Y-%m-%d at %H:%M"), f"{order.kind.id}", order.rendersPath]) + '\n')  # for history
        else:  # job resume
            with open(order.doneLog['url']) as data_renders_log:
                done = data_renders_log.read().split('\n')[1:]  # remove history line from top
                if len(done):
                    if len(done[-1]) == 0:
                        done.pop(-1)  # remove last empty line
                else:
                    print("!! broken done log")
        print(f"!!Done renders before {len(done)}")
        current_job['done_renders'] = done
        current_job['counter'] = 0
    else:
        current_job['done_renders'] = []
        current_job['counter'] = 0

    scene.render.engine = 'BLENDER_EEVEE'  # 'CYCLES'
    scene.render.resolution_x = order.quality.size_x
    scene.render.resolution_y = order.quality.size_y
    scene.render.image_settings.file_format = 'JPEG' if order.quality.ext != 'png' else 'PNG'
    scene.eevee.taa_render_samples = order.quality.samples
    scene.render.image_settings.compression = order.quality.compression if order.quality.compression is not None else 10
    # compression
    # Amount of time to determine best compression: 0 = no compression with fast file output, 100 = maximum lossless compression with slow file output
    # int in [0, 100], default 15

    # stop_file - good choice to pause rendering
    if order.volume > 1:
        open(stop_file, 'w').close()
    print(f"!! scene preparations completed. Volume={order.volume}")
    do_rendering(0, "")  # recursive magic!
    print("do_rendering completed")
    if order.volume > 1:
        os.remove(stop_file) if os.path.exists(stop_file) else None  # work done - we don't need stop file
        if current_job['counter'] > 0:
            print(f"!! finish - Now we make {current_job['counter']} renders. There are {len(current_job['done_renders'])} in done log")
        else:
            print("!! finish - nothing made")
        with open(os.path.join(order.rendersPath, 'finish'), 'w') as fin:
            fin.write(str(current_job['counter']))
        order.status = f"{current_job['counter']} in {datetime.now() - start} s"
        print(f"!! order status: {order.status}")
    else:
        order.renders_posted = 1
    order.running = None
    order.save()
