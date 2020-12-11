import os

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from material.models import Finish, Nature, Pattern, ColorMatchingChart
from wcmatch import pathlib

types = [('table', 'Table'), ('chair', 'Chair'), ('combo', 'Combination'), ('toy', 'Toy'), ]
"""prepared model for rendering"""
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

# class MyModel(models.Model):
#     upload = models.FileField(upload_to=user_directory_path)

from django.core.files.storage import FileSystemStorage
from django.db import models

# DEFAULT_FILE_STORAGE.

fs_blender = FileSystemStorage(location='static/furniture/models/blender')  #settings.RENDER_MACHINE['MODELS_DIR']
fs_glb = FileSystemStorage(location='static/furniture/models/gltf')
fs_sw = FileSystemStorage(location='static/furniture/models/sw')


class Model3D(models.Model):
    """
    describes which 3D models create product images
    """
    name = models.CharField(max_length=32, null=True)  #, unique=True
    #todo fix url in admin
    blend = models.FileField(storage=fs_blender, null=True, blank=True)  # for rendering
    glb = models.FileField(storage=fs_glb, null=True, blank=True)  # for three.js and show on site in realtime
    solidSource = models.FileField(storage=fs_sw, null=True, blank=True)  # source data for our job to convert blender
    updated = models.DateTimeField(auto_now=True, null=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_model_modified')

    @property
    def files(self):
        res = []
        if self.blend:
            res.append('blender')
        if self.glb:
            res.append('threeJS')
        return res

    @property
    def swatch(self):
        products = Product.objects.filter(model_id=self.pk)
        if products:
            return products.first().swatch
        else:
            return "#"

    # @property
    # def natures(self):  # from all kinds
    #     return .objects.filter(model_id=self.pk)


    @property
    def meshes(self):  # from all kinds
        return Mesh.objects.filter(model_id=self.pk).order_by('pk')

    def __str__(self):
        return "[{}] Model3D {} ".format(str(self.pk).zfill(2), self.name)

    # def renders_glob(self, fin_onparts=[], pat_onparts=[] ):  # (part, texture_id)
    #     s = ""
    #     filter = []
    #     for p in Mesh.objects.filter(model_id=self.pk).order_by('id'):
    #         for m_p in fin_onparts:
    #             if p.name in m_p[0]:
    #                 filter.append((p.name, m_p[1]))
    #                 s += f'{p.name}-{m_p[1]}*'
    #                 break
    #
    #     root = pathlib.Path(settings.RENDER_DIR) / str(self.pk)
    #     wild = '*/{done, posted,shadowed}/**.{jpg,png}'
    #     tx_filtered = [str(f)[len(settings.RENDER_DIR) + 1:] for f in root.glob(wild, flags=pathlib.BRACE)]
    #     if not pat_onparts:
    #         return tx_filtered
    #
    #     tx_list = Finish.objects.all().values_list('id', 'pattern_id')
    #     tx_dict = {}
    #     for tx in tx_list:
    #         tx_dict[tx[0]] = tx[1]
    #
    #     for i in range(len(tx_filtered) - 1, -1, -1):  # we have to from end to start for correct removing
    #         pms = os.path.basename(tx_filtered[i]).split('.')[0].split('=')[1].split('_')  # todo save this in the render.Order.model
    #         for pm in pms:
    #             part, tex = pm.split('-')
    #             pattern_id = tx_dict[int(tex)]  # rendered
    #             for pp in pat_onparts:
    #                 if pp[0] == part:
    #                     if pp[1] != pattern_id:
    #                         tx_filtered.pop(i)
    #     return tx_filtered

    def makeglb_fromblend(self):
        pass
        # import bpy
        # from addon_utils import check, enable
        # bpy.ops.wm.read_factory_settings(use_empty=True)
        # for addon in ("io_export_dxf", "io_scene_gltf2"):
        #     default, enabled = check(addon)
        #     if not enabled:
        #         enable(addon, default_set=True, persistent=True)
        # bpy.ops.import_scene.gltf(filepath="/somepath")
        # bpy.ops.export.dxf(filepath="/somefilepath")


    @property
    def api_info(self):
        data = {}
        data['id'] = self.pk
        data['name'] = self.name
        data['meshes'] = list(self.meshes.values_list('name',flat=True))

        # data['meshes'] = [{ "mesh": mesh.name,
        #                     #"cover": list(mesh.cover.all().values_list('name', flat=True)),
        #                     } for mesh in self.meshes]
        return data #json.dumps(data, sort_keys=True, indent=4))


class Mesh(models.Model):
    model = models.ForeignKey(Model3D, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    #optional = models.BooleanField(default=False)
    #cover = models.ManyToManyField(Nature, blank=False)

    #@property
    #def patterns(self):
    #    return Pattern.objects.filter(nature__in=self.cover.all())

    #@property
    #def finishes(self):
    #    return Finish.objects.filter(pattern__nature__in=self.cover.all()).exclude(archive=1)

    def __str__(self):
        return f"{self.model.name}.{self.name}"  # it used in sketchbook - do not change


class Part(models.Model):
    name = models.CharField(max_length=32)  # empty string missed in sketchbook
    meshes = models.ManyToManyField(Mesh, blank=False)  # if colorchart not null  last mesh depended
    cover = models.ManyToManyField(Nature, blank=False)
    comment = models.CharField(max_length=64, default="", blank=True)

    @property
    def model(self):
        if self.modelsCount == 1:
            return self.meshes.all().first().model
        return None

    @property
    def modelsCount(self):
        m = []
        for mesh in self.meshes.all():
            m.append(mesh.model.id)
        return len(list(set(m)))

    @property
    def natures(self):
        return self.cover.all()

    @property
    def displayName(self):
        if self.meshes.all():
            return " & ".join(list(self.meshes.all().values_list('name', flat=True)))
        return "fix! no meshes"

    def __str__(self):
        return f"[{self.model}]{self.displayName}"
        #return f"[{self.meshes.all().first().model.name}] {self.displayName}"
               #f"covered: {list(self.cover.all().values_list('name',flat=True))}"

    # @property
    # def cycle(self):
    #     limits = Limitation.objects.filter(part_id=self.pk)
    #     finishes = {}
    #     if limits:
    #         for lim in limits:
    #             if lim.patterns:
    #                 for p in lim.patterns.all():
    #                     finishes[p.pk] = Finish.objects.filter(pattern=p.pk).exclude(archive=True).values_list('id', flat=True)
    #             if lim.finishes:
    #                 for f in lim.finishes.all():
    #                     pid = f.pattern_id
    #                     if pid not in finishes:
    #                         finishes[pid] = []
    #                     finishes[pid].append(f.pk)
    #     else:
    #         patterns = Pattern.objects.filter(nature__in=self.cover.all()).values_list('id', flat=True)
    #         for p in patterns:
    #             finishes[p] = Finish.objects.filter(pattern=p).exclude(archive=True).values_list('id', flat=True)
    #     res = {
    #         'meshes': self.meshes.all(),
    #         'finishes': finishes,
    #         'part_id': self.pk,
    #         }
    #     if self.colorChart:
    #         res['colorChart_id'] = self.colorChart.id
    #     return res

    # @property
    # def cycle_str(self):
    #     meshes = ','.join([m.name for m in self.meshes.all()])
    #     mats = ','.join([m.name for m in self.cover.all()])
    #     limits = Limitation.objects.filter(part_id=self.pk)
    #     if len(limits):
    #         return f"{meshes}:[{' '.join([str(l) for l in limits])}]"
    #     else:
    #         return f"{meshes}:{mats}"


class Product(models.Model):
    name = models.CharField(max_length=64)
    model = models.ForeignKey(Model3D, on_delete=models.PROTECT, null=True)
    producer = models.CharField(max_length=32)
    product_code = models.CharField(max_length=32, null=True, blank='')
    type = models.CharField(max_length=5, choices=types)
    collection = models.CharField(max_length=32)
    swatch = models.ImageField(upload_to='static/furniture/swatches',
                               height_field=None, width_field=None, max_length=100, null=True, blank=True)

    @property
    def rendersPath(self):
        return os.path.join(settings.MEDIA_ROOT, str(self.model.id))

    @property
    def qualities(self):
        from render.models import Quality
        res = []
        rp = self.rendersPath
        print(rp)
        for q in os.listdir(rp):
            print(q)
            if os.path.isdir(os.path.join(rp, q)):
                try:
                    res.append(Quality.objects.get(pk=int(q)))
                except:
                    pass
        return res


    @property
    def diskSize(self):
        return get_kbsize(self.rendersPath)

    @property
    def kinds(self):  # from all kinds
        return ProductKind.objects.filter(product_id=self.pk)

    @property
    def orders(self):  # from all kinds
        from render.models import Order
        return Order.objects.filter(kind__product_id=self.pk)

    @property
    def parts(self):  # from all kinds
        res = set()
        for k in self.kinds:
            res |= set(k.parts.all())
        return sorted(res, key=lambda x: x.id)

    @property
    def partNames(self):  # from all kinds
        res = set()
        for k in ProductKind.objects.filter(product_id=self.pk):
            res |= set(k.parts.all().values_list('name', flat=True))
        return sorted(res)  # by name

    def __str__(self):
        return f"[{self.id}] {self.name}, [{self.product_code}]" # producer: {self.producer}

    def external_url(self):
        return mark_safe(u'<a href="{0}" target="_blank">memo sketchbook</a>'.format(
            f'http://sketchbook.memofurniture.com/?product_code={self.product_code}'))

    def swatch_link(self):
        return mark_safe(u'<a href="{0}" target="_blank"><img src="/{0}" width="100"/></a>'.format(self.swatch))

    @property
    def renders(self):
        root = pathlib.Path(settings.MEDIA_ROOT) / str(self.model.id)

        wild1 = '*/*.{jpg,png}' # posted
        wild2 = 'orders/*/*/*.{jpg,png}' # done
        #wild = '*/{done,posted,shadowed}/**.{jpg,png}'
        #return [str(f)[len(settings.MEDIA_ROOT) + 1:].replace('\\', '/') for f in root.glob(wild, flags=pathlib.BRACE)]
        return [str(f)[len(settings.MEDIA_ROOT) + 1:].replace('\\', '/') for f in root.glob(wild1, flags=pathlib.BRACE)]

    @property
    def rendersInOrders(self):
        root = pathlib.Path(settings.MEDIA_ROOT) / str(self.model.id)
        wild2 = 'orders/*/*/*.{jpg,png}'  # done
        return [str(f)[len(settings.MEDIA_ROOT) + 1:].replace('\\', '/') for f in root.glob(wild2, flags=pathlib.BRACE)]

    # @property
    # def rendersDiskSize(self):
    #     return sum([order.diskSize for order in self.orders])  #kb->Mb

    def usedNatures(self, partname=''):
        natures = set()
        for p in ProductKind.objects.filter(product_id=self.pk):
            natures |= set(p.usedNatures(partname))
        return sorted(natures, key=lambda x: x.id)

    @property
    def patterns(self):
        res = set()
        for conf in Configuration.objects.filter(kind__product=self.pk):
            res |= set(conf.patterns)
        return list(res)

    @property
    def usedFinishes(self):
        finishes = set()
        for c in Configuration.objects.filter(kind__product=self.pk):
            finishes |= set(c.finishes)
        return list(finishes)


class ProductKind(models.Model):
    name = models.CharField(max_length=64)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    #model = models.ForeignKey(Model3D, on_delete=models.PROTECT)  # todo check every part connect to this model through all its meshes -> make a @propery
    comment = models.CharField(max_length=128, blank=True, null=True)
    parts = models.ManyToManyField(Part, blank=True, through='Configuration')

    def __str__(self):
        return f'[{self.pk}]{self.name}'

    @property
    def cycles(self):
        return [c for c in Configuration.objects.filter(kind=self.pk).order_by('id')]

    @property
    def renderOrderTemplate(self):
        conf = '-'.join([p.name+":{}" for p in self.renderOrderParts])
        return f"config={conf}"
        #     return ';'.join([p.cycle_str for p in self.parts.all()])

    @property
    def ruleTemplate(self):
        return ';'.join([p.name+":*" for p in self.renderOrderParts])

    @property
    def renderOrderParts(self):
        return [c.part for c in Configuration.objects.filter(kind=self.pk).order_by('id') if not c.colorChart_id]
    # @property
    # def rule(self):
    #     return self.renderOrderTemplate.split("=")[1].replace("{}","*").replace('-',';')

    @property
    def orders(self):
        from render.models import Order
        return Order.objects.filter(kind_id=self.id)

    # def partNameByMeshName(self, mesh_name):
    #     index = self.indexInOrderByMeshName(mesh_name)
    #     return self.parts.all()[index].name if index >= 0 else ""

    def deep(self, mesh_name):
        for index, c in enumerate(self.cycles):
            for m in c.part.meshes.all():
                if m.name == mesh_name:
                    return index
        return -1

    @property
    def patterns(self):
        res = set()
        for conf in Configuration.objects.filter(kind=self.pk):
            res |= set(conf.patterns)
        return list(res)

    # def partByMeshName(self, mesh_name):
    #     for index, c in enumerate(self.cycles):
    #         for m in c.part.meshes.all():
    #             if m.name == mesh_name:
    #                 return c.part
    #     return None

    def filename(self, finishes):
        f = self.product.model.name + '='
        for mesh in self.product.model.meshes:
            deep = self.deep(mesh.name)
            finish_id = '0'
            if deep >= 0:
                finish_id = finishes[deep] # NONE_FINISH.id set to 0 before
            f += f"{mesh.name}-{finish_id}_"
        return f[:-1]

    @property
    def api_info(self):
        data = {}
        data['id'] = self.pk
        data['name'] = self.name
        data['configuration'] = [ {"part": c.part.name,
                                   "defaultfinish": c.defaultFinish_id,
                                   #todo add GUI displayname
                                   "optional": c.optional,
                                   "limited": c.limitation_id,
                                   "colorchart": c.colorChart_id,
                                   "covered": list(c.part.cover.all().values_list('name', flat=True)),
                                   "finishes": [f.id for f in c.finishes]}
                  for c in Configuration.objects.filter(kind=self.pk).order_by('id')]
        #data['render-template'] = 'config=' + '-'.join([ d["part"] + ":{}" for d in data['configuration'] if not d['colorchart']])
        return data #json.dumps(data, sort_keys=True, indent=4))


    def parse_rules(self, pairs, only_one=0):
        try:
            template = self.api_info['configuration']
            conf = {}
            parts = {}
            if len(pairs) != len(self.renderOrderParts):
                return {"error": f"You must specify {len(self.renderOrderParts)} parts, not {len(pairs)}. use template: {self.renderOrderTemplate}"}
            for pair in pairs:
                p, m = pair.split(':')
                if only_one:
                    conf[p.lower()] = int(m)
                else:
                    conf[p.lower()] = 0 #m
                    # need to parse * 1,2,3 p1,2 etc

            config = Configuration.objects.filter(kind=self.pk).order_by('id')
            for i, c in enumerate(config):
                for mesh in c.part.meshes.all():
                    parts[mesh.name] = c.part.name.lower()
                part = c.part.name.lower()
                if part not in conf:
                    if c.colorChart_id:
                        prev_part = config[i-1].part.name.lower()
                        if only_one:
                            matches = c.colorChart.match(conf[prev_part])
                            if len(matches):
                                conf[part] = matches[0].id  # find one by colorchart
                                continue
                            return {"error": f"there is no match finish for {part} based on {prev_part}:{conf[prev_part]} by colorchart {c.part.colorChart_id}"}
                        else:
                            conf[part] = 0
                    else:
                        return {"error": f"You missed {part} in your request "}
                if not conf[part]:
                    if not c.optional and only_one:
                        return {"error": f"{part} is not optional - you have to choose suited material finish id"}
                    continue
                if only_one:
                    finish = Finish.objects.get(pk=int(conf[part]))
                    pattern = finish.pattern
                    nature = pattern.nature
                    if nature not in c.part.cover.all():
                        return {"error": f"You can't use {nature} [{finish.id}]for {part}, you have to use {[f.id for f in c.finishes]}. to get info about correct finishes use api"}
                    #return {"error": f"You can't use {nature} [{finish.id}]for {part}, you have to use {list(c.part.cover.all().values_list('name', flat=True))}. to get info about correct finishes use api"}
                    # todo check only: [f.id for f in c.finishes]
                    if c.limitation_id:
                        found = False
                        if c.limitation.patterns.all():
                            found = (pattern.id in list(c.limitation.patterns.all().values_list('id', flat=True)))
                        if c.limitation.finishes.all():
                            found = (finish.id in list(c.limitation.finishes.all().values_list('id', flat=True)))
                        if not found:
                            return f"finish {finish.id} from pattern {pattern.id} not suited on limitation {c.limitation} for part {part}. USE one of {[f.id for f in c.finishes]}"
            ## all is OK, calc filename!
            meshes_str = '_'.join([f"{mesh.name}-" + (f"{conf[parts[mesh.name]]}" if mesh.name in parts else "0") for mesh in self.product.model.meshes])
            return {"file": f"{self.product.model.name}={meshes_str}"}  # without .jpg/ .png
        # .png
        except Exception as err:
            print(repr(err))
            raise err
            return {"error": repr(err)}
    # def config2post(self, fn):
    #     pairs = fn.split("=")[1]
    #     conf = {}
    #     for pair in pairs.split('_'):
    #         mesh, mat = pair.split("-")
    #         if mat == 0:
    #             continue
    #         part = self.partByMeshName(mesh)
    #         if not len(part):
    #             return ''
    #         if part in conf:
    #             if mat != conf[part]:
    #                 return ''
    #         else:
    #             conf[part] = mat
    #     return '-'.join([f"{p}:{m}" for p, m in conf.items()])



    def usedNatures(self, partname=''):
        natures = set()
        for p in self.parts.all():
            if len(partname) and p.name != partname:
                continue
            natures |= set(p.cover.all())
        return list(natures)

    @property
    def usedFinishes(self):
        finishes = set()
        for c in Configuration.objects.filter(kind=self.pk):
            finishes |= set(c.finishes)
        return list(finishes)


class Limitation(models.Model):
    # nature check
    name = models.CharField(max_length=32, null=True)
    patterns = models.ManyToManyField(Pattern, blank=True)
    finishes = models.ManyToManyField(Finish, blank=True)

    def __str__(self):
        pids = ' '.join([f'p{p.id}' for p in self.patterns.all()]) #.filter(nature=mat)
        ids = ' '.join([f'{f.id}' for f in self.finishes.all()]) #.filter(pattern__nature=mat)
        return (self.name if self.name else "") + (':' + ' '.join([pids, ids])) if len(pids)+len(ids) else ""


class Configuration(models.Model):
    kind = models.ForeignKey(ProductKind, on_delete=models.PROTECT)
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    optional = models.BooleanField(default=False, blank=True)
    limitation = models.ForeignKey(Limitation, on_delete=models.PROTECT,  blank=True, null=True)
    colorChart = models.ForeignKey(ColorMatchingChart, on_delete=models.PROTECT, blank=True, null=True)
    defaultFinish = models.ForeignKey(Finish, on_delete=models.PROTECT, blank=True, null=True)

    @property
    def patterns(self):
        if self.limitation:
            if self.limitation.patterns:
                return self.limitation.patterns.all()
            return []  #todo pattern from finishes
        res = []
        for nature in self.part.cover.all():
            res += nature.patterns
        return res

    @property
    def finishes(self):
        res = []
        if self.limitation:
            if self.limitation.patterns:
                for p in self.limitation.patterns.all():
                    res += p.finishes
            if self.limitation.finishes:
                res += self.limitation.finishes.all()
            return res

        for nature in self.part.cover.all():
            res += nature.finishes
        return res

    @property
    def cycle(self):
        mats = ''
        if self.colorChart:
            return ""
        if self.limitation:
            if self.limitation.patterns:
                mats += ' '.join([f"p{p.id}" for p in self.limitation.patterns.all()])
            if self.limitation.finishes:
                mats += ' ' + ' '.join([f"{p.id}" for p in self.limitation.finishes.all()])
        if len(mats) <= 1:
            mats='*'
        return f"{self.part.name}:{mats}"

    @property
    def N(self):
        if self.colorChart:
            return 1
        return len(self.finishes) + (1 if self.optional else 0)

    # def match(self, prev):
    #     suited = []
    #     if self.colorChart:
    #         for match in ColorMatch.objects.filter(chart_id=self.colorChart.pk).all():
    #             if str(prev) in match.suited.split(','):
    #                 suited.append(match.finish_id)
    #     return suited

# todo: сделать нотификации при добавлении важных объектов ( таких как новая модель)
# def notify_admin(sender, instance, created, **kwargs):
#     '''Оповещает администратора о добавлении новой модели.'''
#     if created:
#         subject = 'New model 3d created'
#         message = 'model3d %s was added' % instance.name
#         from_addr = 'django@example.com'
#         recipient_list = ('grigorenko.tihon@gmail.com',)
#         send_mail(subject, message, from_addr, recipient_list)
#
#
# signals.post_save.connect(notify_admin, sender=Model3D)



def get_kbsize(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            if os.path.isfile(os.path.join(dirpath, f)):
                total_size += os.path.getsize(os.path.join(dirpath, f))
    return total_size >> 10  # размер в килобайтах