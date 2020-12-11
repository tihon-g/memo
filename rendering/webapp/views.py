import json
import os
from wcmatch import pathlib

import pika
#from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.static import serve
from furniture.models import Model3D, Product, ProductKind, Limitation
from material.models import Finish, Pattern, Nature, ColorMatchingChart, ColorMatch
from render.models import Order, Quality, Machine

from .forms import CreateUserForm, LoginUserForm

#import rendering.digitalocean as do

# main homepage
#@login_required

# if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3' and 'HOST' in settings.RENDER_MACHINE['POSTING']:
#     import psycopg2
#     conn = psycopg2.connect(dbname=settings.RENDER_MACHINE['POSTING']['NAME'],
#                             user=settings.RENDER_MACHINE['POSTING']['USER'],
#                             password=settings.RENDER_MACHINE['POSTING']['PASSWORD'],
#                             host=settings.RENDER_MACHINE['POSTING']['HOST'],
#                             port=settings.RENDER_MACHINE['POSTING']['PORT'])
#     conn.autocommit = True
#     do_db = conn.cursor()

def index(request):
    context = {
        #'meshes': Mesh.objects.filter(model__glb__isnull=False),
        #'finishes': Finish.objects.exclude(name__isnull=True),
        #'hdrmaps': [os.path.basename(f) for f in
       #            Path(os.path.join(settings.STATIC_ROOT, 'furniture', 'models', 'hdri')).glob("*.hdr")],  # todo from db
        #'data': {},
    }

    if request.method == 'POST':
        pass
        # messages.add_message("post: " + request.POST)
        # data = .. to do pass back data from POST to form

    return render(request, 'home.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip() # цепочка прокси ( исп последнюю )
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def regPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid:
            try:
                form.save()
                #user = form.changed_data.get("username")
                user = form.cleaned_data['username']
                pswd = form.cleaned_data['password1']
                # return redirect('login')
                # Below 2 lines, if you want user to get logged in
                user = authenticate(username=user, password=pswd)
                login(request, user)
                messages.add_message(request, messages.SUCCESS,  f"Account created for {user}")
                return redirect('homepage')
            except ValueError as e:
                messages.add_message(request, messages.ERROR, f"Can't create account {e}")

        else:
            form = CreateUserForm(request.POST)

    return render(request, "webapp/signup.html", {'form': form})


#@csrf_protect
def loginPage(request):
    form = LoginUserForm(data=request.POST)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
            # Redirect to a success page.
            #...
        else:
            pass
            # Return an 'invalid login' error message.
            #...

    return render(request, 'webapp/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'webapp/profile.html', {'user': request.user})


def logoutPage(request):
    logout(request)
    return redirect('homepage')

################################### API ##################################
# https://webdevblog.ru/sozdanie-django-api-ispolzuya-django-rest-framework-apiview/
# but i am not using it

def api_model_index(request):
    return JsonResponse({"models": [m.api_info for m in list(Model3D.objects.exclude(blend__isnull=True).order_by('id'))]}, status=200)
#     return JsonResponse(Model3D.objects.all().values_list('id', 'name')).filter(id__gt=24)

def api_product_index(request):
    return JsonResponse({"products": list(Product.objects.exclude(model__blend__isnull=True).order_by('id').
                                    values('id', 'name', 'product_code', 'collection', 'type', 'model_id'))
                         }, status=200)


def api_product_kinds(request, product_id):
    return JsonResponse({"styles": [kind.api_info for kind in ProductKind.objects.filter(product=product_id)]}, status=200)


def api_product_kind_details(request, product_id, kind_id):
    try:
        kind = ProductKind.objects.get(pk=kind_id)
        if kind.product_id != product_id:
            return JsonResponse({"error": f"Product {product_id} don't have style with id={kind_id}"}, status=400)
        return JsonResponse(kind.api_info, status=200)
    except:
        return JsonResponse({"error": f"there is no style with id={kind_id}"}, status=400)


def api_pattern_index(request):
    data = {}
    for nature_id, nature in Nature.objects.all().values_list('id', 'name'):
        data[nature] = []
        for p in Pattern.objects.filter(nature=nature_id):
            data[nature].append({'id': p.id, 'name': p.name, 'squ': p.squ, 'finishes': len(p.finishes)})
        if not len(data[nature]):
            del data[nature]
    return JsonResponse(data, status=200)

#@api_view(['GET'])
def api_pattern_details(request, pattern_id):
    if request.method != 'GET':
        return JsonResponse({"error": "use get method"} )
    finishes = Pattern.objects.get(pk=pattern_id).finishes
    data = []
    for f in finishes:
        data.append({'id': f.id, 'squ': f.squ})
    return JsonResponse({"finishes": data}, status=200)

# def api_render(request, product_id, rule):
#     prod = Product.objects.get(pk=product_id)
#     if request.method == 'POST':
#         # todo
#         return JsonResponse({"error": "Later you can use this request for upload render image"})
#     elif request.method == 'GET':
#
#         return JsonResponse({"status": f"Later I can return render image with config {request.GET['config']}"})
#     else:
#         return JsonResponse({"error": f"use config {prod.config}"})


def api_get_render(request):  #todo must pass quality here
    if request.method != 'GET':
        return JsonResponse('only GET method supported', safe=False, status=500)
    # kind == style
    if 'style' not in request.GET:
        return JsonResponse('must specify product style', safe=False, status=400)
    kind = None
    try:
        kind = ProductKind.objects.get(pk=request.GET['style'])
    except:
        return JsonResponse({"error": f"there is no style with id {request.GET['style']}"})

    # quality
    q = None
    if 'quality' in request.GET:
        try:
            q = Quality.objects.get(pk=request.GET['quality'])
        except:
            return JsonResponse('there is no such quality', safe=False, status=400)

    # config
    if 'config' not in request.GET:
        return JsonResponse('must specify config', safe=False, status=400)

    res = kind.parse_rules(request.GET['config'].split('-'), 1)  # only config parsing
    if "error" in res:
        return JsonResponse(res, status=400)
    if "file" in res:
        if q:
            file_path = os.path.join(str(kind.product.model.id), str(q.id), f"{res['file']}.{q.ext}")
            media = os.path.join(settings.MEDIA_ROOT, file_path) #jpg/png
            if os.path.exists(media):
            #media_url = os.path.join('/', settings.X_ACCEL_REDIRECT_PREFIX, file_path)  # os.path.join(settings.MEDIA_URL, file_path)
                return serve(request, file_path, settings.MEDIA_ROOT)
        else:
            product_root = pathlib.Path(os.path.join(settings.MEDIA_ROOT, str(kind.product.model.id)))
            wild = f"*/{res['file']}" + ".{jpg,png}"
            filtered = list(product_root.glob(wild, flags=pathlib.BRACE))
            if filtered:
                # first one
                return serve(request, os.path.relpath(filtered[0], settings.MEDIA_ROOT), settings.MEDIA_ROOT)
        # need to render
        o_rule = request.GET['config'].replace('-', ';')
        # create new order
        try:
            order = Order.objects.filter(kind=kind).filter(running__isnull=False).get(rule=o_rule)  # double click
            # if i have the same order in queue or running
        except:
            order = Order()
            order.kind_id = kind.id
            order.rule = o_rule
            try:
                order.quality_id = Quality.objectsget(pk=int(os.getenv('QUALITY'))).id
            except:
                order.quality_id = 1
            # todo put it (calc path) in the model
        file_path = os.path.join(str(kind.product.model.id), str(order.quality.id), f"{res['file']}.{order.quality.ext}")

        status = order.run()
        if status == 'ok':
            return render(request, 'webapp/render.html', {"order": order, "file_path": file_path})
        else:
            return JsonResponse({"mqtt error": status}, safe=False, status=500)

    return JsonResponse(res, safe=False, status=500)

def api_render_info(request):
    res = {}
    for k in ProductKind.objects.all():
        res[k.id] = {'name': k.name, 'product_id': k.product_id, 'config': k.renderOrderTemplate}
    return JsonResponse(res, status=200)

def api_limitations(request):
    res = {}
    for lim in Limitation.objects.all():
        res[lim.id] = {'patterns': [(p.id, p.name) for p in lim.patterns.all()], 'finishes': [(f.id, f.squ) for f in lim.finishes.all()]}
    return JsonResponse(res, status=200)

def api_colorcharts(request):
    res = {}
    for ch in ColorMatchingChart.objects.all():
        res[ch.id] = [{'match': m.finish.id, 'suited': m.suited} for m in ColorMatch.objects.filter(chart=ch.id)]
    return JsonResponse(res, status=200)

def api_get_finish(request, finish_id):
    return serve(request, Finish.objects.get(pk=finish_id).diffuse_relpath, settings.STATIC_ROOT)

def api_quality_index(request):
    return JsonResponse({"qualities": list(Quality.objects.order_by('id').
                                    values('id', 'size_x', 'size_y', 'ext', 'compression'))
                         }, status=200)