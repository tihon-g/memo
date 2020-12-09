import json
from django.contrib import messages
from django.core.management import call_command
from django.shortcuts import render, redirect

from .models import Product, ProductKind, Model3D, Mesh

def index(request, selected_collection=""):
    return render(request, 'index.html', {'products': Product.objects.exclude(type="toy"),
                                          'selected_collection': selected_collection,
                                          'nav_active': 'furniture'})


def product_details(request, product_id):
    if request.method == 'POST':
        obj = Model3D.objects.get(pk=Product.objects.get(pk=product_id).model.id)
        if 'gltf' in request.FILES:
            glbfile = request.FILES['gltf']
            obj.glb = glbfile
        if 'blend' in request.FILES:
            blendfile = request.FILES['blend']
            obj.blend = blendfile
            obj.save()
            try:
                res = call_command('check_model', obj.id)
                messages.add_message(request, messages.INFO, res)
                # todo modal form with new meshes to add
                return redirect('furniture:add-meshes', product_id, res)
            except Exception as e:
                obj.blend.delete()
                obj.blend = None
                obj.save()
                messages.add_message(request, messages.ERROR, repr(e))

        # fs = FileSystemStorage()
        # filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)
    return render(request, 'details.html',  {'product': Product.objects.get(pk=product_id),
                                             'kinds': ProductKind.objects.filter(product_id=product_id),
                                             'nav_active': 'furniture'})


def add_meshes(request, product_id, json_meshes):
    #json_meshes = request.query_params['json']
    data = json.loads(json_meshes)
    m = Model3D.objects.get(pk=Product.objects.get(pk=product_id).model.id)

    if request.method == 'POST':
        if 'delete-model' in request.POST:
            #m.delete()
            messages.add_message(request, messages.INFO, 'bad idea to delete model')
        if 'save-meshes' in request.POST:
            added = []
            for k,v in data.items():
                if k in request.POST:
                    mesh = Mesh()
                    mesh.name=k
                    mesh.model_id=m.id
                    mesh.save()
                    added.append(k)
            if len(added):
                messages.add_message(request, messages.SUCCESS, f"meshes: {','.join(added)} added into model {m.name}")
            else:
                messages.add_message(request, messages.INFO, 'no any mesh added')
        return redirect('furniture:details', product_id)
    return render(request, 'add_meshes_form.html', {'model': m,
                                                    'meshes': Mesh.objects.filter(model_id=m.id),
                                                    'meshes_json': data})
