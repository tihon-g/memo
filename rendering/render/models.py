import math
import os
import shutil
import subprocess
from datetime import datetime

from concurrency.fields import AutoIncVersionField
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.timezone import make_aware
from furniture.models import ProductKind, Model3D
from furniture.models import get_kbsize
from material.models import Pattern, Finish
# import rendering.digitalocean as do
# from furniture.models import Part
# from material.models import Nature, Pattern, Finish
from wcmatch import pathlib
from render.utils import execute_wait


# stdout
# When you are using management commands and wish to provide console output, you should write to self.stdout and self.stderr,
# instead of printing to stdout and stderr directly. By using these proxies, it becomes much easier to test your custom command.
# Note also that you don’t need to end messages with a newline character, it will be added automatically, unless you specify the ending parameter:

# todo Eсли хотите из одного процесса выходные данные передать на вход другого процесса, то можно так:
#
# p1 = Popen('python ex1.py' stdout=PIPE)
# p2 = Popen('python ex2.py' stdin=p1.stdout)
# def execute_wait(com):
#     proc = subprocess.Popen(com, shell=False, stdout=subprocess.PIPE, universal_newlines=True)
#     # windows Warning : Using shell = True can be a security hazard
#     # Note Do not use stdout=PIPE or stderr=PIPE with this function as that can deadlock based on the child process output volume. Use Popen with the communicate() method when you need pipes.
#     # subprocess.run(["ls", "-l", "/dev/null"], capture_output=True)
#     for stdout_line in iter(proc.stdout.readline, ""):
#         yield stdout_line
#     proc.stdout.close()
#     return_code = proc.wait()
#     if return_code:
#         print(f"proc failed - {subprocess.CalledProcessError(return_code, com)}")


class Quality(models.Model):
    samples = models.PositiveIntegerField(null=True, default=128, validators=[MinValueValidator(32), MaxValueValidator(512)])
    size_x = models.PositiveIntegerField(null=True, default=1250, validators=[MinValueValidator(128), MaxValueValidator(2500)])
    size_y = models.PositiveIntegerField(null=True, default=1000, validators=[MinValueValidator(100), MaxValueValidator(2000)])
    engine = models.CharField(choices=[('BLENDER_EEVEE', 'eevee'), ('CYCLES', 'cycles')], max_length=13, default='BLENDER_EEVEE')
    compression = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(100)])
    ext = models.CharField(choices=[('jpg', 'JPEG'), ('png', 'PNG')], max_length=13, default='jpg')
    def __str__(self):
        return f"{self.ext} {self.size_x}x{self.size_y} with {self.samples} samples " # and {self.compression} compression"

class Camera(models.Model):
    name = models.CharField(null=True, max_length=32)
    orth = models.BooleanField(default=False)
    focus = models.PositiveIntegerField(validators=[MinValueValidator(15), MaxValueValidator(120)], default=60)
    # position
    phi = models.FloatField(default=0.0) #, validators=[MinValueValidator(-179), MaxValueValidator(180)])
    theta = models.FloatField(default=1.4)  #, validators=[MaxValueValidator(90)])
    r = models.FloatField(default=6.0, validators=[MinValueValidator(1.0), MaxValueValidator(10.0)], null=True)
    # # lookAt
    lookAt_x = models.FloatField(default=0)
    lookAt_y = models.FloatField(default=0)
    lookAt_z = models.FloatField(default=0)

    @classmethod
    def calc_angles(cls, loc):
        r = math.sqrt(sum([c*c for c in loc]))
        return (r,
                math.atan2(loc[1], loc[0]),
                math.atan2(r, loc[2])
        )

    @property
    def location_dict(self):
        p = self.r*math.sin(self.theta)
        return {'x': self.r * math.sin(self.theta) * math.cos(self.phi),
                'y': self.r * math.sin(self.theta) * math.sin(self.phi),
                'z': self.r * math.cos(self.theta),
                }
    @property
    def location(self):
        p = self.r*math.sin(self.theta)
        return (self.r * math.sin(self.theta) * math.cos(self.phi),
                self.r * math.sin(self.theta) * math.sin(self.phi),
                self.r * math.cos(self.theta),
                )

    def set_angles(self, coords):
        self.r, self.phi, self.theta = Camera.calc_angles(coords)

    def set_lookAt(self, coords):
        self.lookAt_x, self.lookAt_y, self.lookAt_z = tuple(coords)

    @property
    def lookAt(self):
        return (self.lookAt_x, self.lookAt_y, self.lookAt_z)

class Scene(models.Model):
    name = models.CharField(null=True, max_length=32)
    world = models.FileField(null=True)
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True)
    quality = models.ForeignKey(Quality, null=True, on_delete=models.PROTECT)
    img = models.FileField(null=True, upload_to='scenes/')
    status = models.CharField(null=True, blank=True, max_length=32)
    worker = models.ForeignKey('Machine', null=True, blank=True, on_delete=models.SET_NULL)
    version = AutoIncVersionField()
    # img = models.FileField(null=True, upload_to=f'{settings.MEDIA_URL[1:]}/scenes')

    def orderRender(self, engine='Eevee'):
        pass


class Actor(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.SET_NULL, null=True)
    #kind = models.ForeignKey(ProductKind, on_delete=models.PROTECT) #<- order string here
    model = models.ForeignKey(Model3D, on_delete=models.PROTECT, null=True) #<- order string here
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    rotation_z = models.PositiveIntegerField(default=0)
    scale = models.FloatField(default=1)
    # one string for all parts
    finishesOnMeshes = models.CharField(max_length=2048, default="")  # or finishes on Meshes

    def set_position(self, coords):
        self.position_x, self.position_y, self.rotation_z = tuple(coords)


class Order(models.Model):
    kind = models.ForeignKey(ProductKind, null=True, on_delete=models.PROTECT)
    quality = models.ForeignKey(Quality, null=True, on_delete=models.PROTECT)
    rule = models.CharField(null=True, max_length=1024, blank=True)
    running = models.BooleanField(null=True)  # 0 - в очереди, #1 - выполняется, #null - не требует запуска
    renders_done = models.PositiveIntegerField(default=0)
    renders_posted = models.PositiveIntegerField(default=0)
    status = models.CharField(null=True, blank=True, max_length=32)
    volume = models.PositiveIntegerField(default=0, null=True, blank=True)
    worker = models.ForeignKey('Machine', null=True, blank=True, on_delete=models.SET_NULL)
    version = AutoIncVersionField()

    @property
    def model(self):
        return self.kind.product.model

    def run(self):
        # sending to rabbitMQ
        if os.getenv('RABBIT_HOST'):
            # put message into rabbit
            try:
                import pika, json
                credentials = pika.PlainCredentials(os.getenv('RABBIT_USER'), os.getenv('RABBIT_PASSWORD'))
                parameters = pika.ConnectionParameters(os.getenv('RABBIT_HOST'), os.getenv('RABBIT_PORT'), os.getenv('RABBIT_VIRTUALHOST', default='/'), credentials=credentials)
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                data = {'model': str(self.kind.product.model.blend), 'order_id': str(self.pk)}  # , 'rule': self.rule, 'quality': self.quality
                channel.basic_publish(exchange='', routing_key='orders', body=json.dumps(data))
                connection.close()
                self.running = False  # put to queue
                self.volume = self.N
                self.save()
                # if success - save it
                return 'ok'
            except Exception as err:
                self.running = None
                self.save()
                print(f'MQTT ERROR {repr(err)}')
                return repr(err)
        else:
            self.running = False  # put to queue
            self.volume = self.N
            self.save()
            return "RABBIT_HOST missed in the env! but if queue command looks in db - it can be run because it in the queue"

    def cancel(self):
        try:
            self.running = None
            if not self.renders_done:
                self.worker = None
            self.save()
        except:
            print("concurrent access to order - can't cancel")
            pass

    def cleanData(self):
        shutil.rmtree(self.rendersPath)
        self.renders_done = 0
        self.worker = None
        self.save()

    def postData(self, copy_type):
        src = os.path.join(self.rendersPath, str(self.quality.id))
        dest = os.path.join(self.kind.product.rendersPath, str(self.quality.id))
        if not os.path.exists(dest):
            os.makedirs(dest)
        for f in os.listdir(src):
            if f[0] != '.' and os.path.isfile(os.path.join(src, f)):
                if (copy_type == 'copy'):
                    shutil.copyfile(os.path.join(src, f), os.path.join(dest, f))
                elif (copy_type == 'move'):
                    shutil.move(os.path.join(src, f), os.path.join(dest, f))
                else: #sym
                    os.symlink(os.path.join(src, f), os.path.join(dest, f))

    # very useful for rendering!
    @property
    def cycles(self):
        result = []
        if not self.kind:
            return result
        config = self.kind.cycles
        rules = {}
        if self.rule:
            for r in self.rule.split(';'):
                pr = r.split(':')
                rules[pr[0].lower()] = pr[1]
        for conf in config:
            cycle = {'config': conf, 'meshes': conf.part.meshes.all().values_list('name', flat=True), 'finishes': []}
            if not conf.colorChart:
                rule = rules[conf.part.name.lower()] if conf.part.name.lower() in rules else "*"
                try:
                    # finishes by comma
                    cycle['finishes'] = [Finish.objects.get(pk=int(f)) for f in rule.split(',')]
                except:
                    if conf.optional:  # + (1 if c['config'].optional else 0)
                        cycle['finishes'].append(Finish.objects.get(pattern__nature__name='none'))
                    if rule == "*":
                        cycle['finishes'] += sorted([f for f in conf.finishes], key=lambda f: f.pattern_id)
                    elif rule[0] == 'p':
                        p_id = int(rule[1:])
                        cycle['finishes'] += Pattern.objects.get(pk=p_id).finishes

            result.append(cycle)
        return result

    @property
    def N(self):
        res = 1
        for c in self.cycles:
            if c['config'].colorChart:
                continue
            res *= len(c['finishes'])
        return res

    def clone(self):
        o = Order()
        o.kind = self.kind
        o.shadow = self.shadow
        o.quailty = self.quailty
        #o.N = 0
        return o

    def get_absolute_url(self):
        return reverse('order-update', kwargs={'order_id': self.pk})

    @property
    def rendersPath(self):
        return os.path.join(self.kind.product.rendersPath, 'orders', str(self.pk))

    @property
    def relRendersPath(self):
        return os.path.join(self.kind.product.relRendersPath, 'orders', str(self.pk))
    # @property
    # def donePath(self):
    #     return os.path.join(self.rendersPath, "done")


    @property
    def diskSize(self):
        try:
            return get_kbsize(self.rendersPath)
        except:
            return 0

    @property
    def renders(self):
        wild = '**/*.{jpg,png}'
        return [str(f)[len(settings.MEDIA_ROOT) + 1:].replace('\\', '/') for f in pathlib.Path(self.rendersPath).glob(wild, flags=pathlib.BRACE)]

    # @property
    # def renderDirs(self): # for show data contents in the order
    #     dirs = {}
    #     wild = "**.*"
    #     # todo use Path instgead of os.path https://docs.python.org/3/library/pathlib.html
    #     if os.path.exists(self.rendersPath):
    #         for d in os.listdir(self.rendersPath):
    #             if d[0] == '.':
    #                 continue
    #             dd = os.path.join(self.rendersPath, d)
    #             if os.path.isdir(dd):
    #                 dirs[d] = len(list(pathlib.Path(dd).glob(wild)))
    #     return dirs

    @property
    def doneLog(self):
        url = os.path.join(self.rendersPath, f'order-{self.pk}.log')
        try:
            with open(url) as done_log:
                done_renders = done_log.read().split('\n')
                head = done_renders.pop(0)
                if len(done_renders[-1]) == 0:
                    done_renders.pop(-1)
                return {'url': url, 'count': len(done_renders), 'started': head.split('\t')[0]}
        except:
            return {'url': url}

    # def url(self, key=""):
    #     if self.N > 1 or not self.renders_done:
    #         return ''
    #     if not key:
    #         key = self.kind.parse_rules(self.rule.split(';'))['file']
    #     try:
    #         do.s3.Object(settings.AWS_STORAGE_BUCKET_NAME, key).load()
    #         return do.s3client.generate_presigned_url(ClientMethod='get_object',
    #                                          Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
    #                                                  'Key': key},
    #                                          ExpiresIn=600)
    #     except:
    #         return ""

    def __str__(self):
        return f"[{self.pk}]order for product kind {self.kind}, {self.quality}, rules:'{self.rule}' volume={self.N}"

    # def get_absolute_url(self):
    #     """
    #     Returns the url to access a particular instance of the model.
    #     """
    #     return reverse('render:order-edit', args=[self.model.id, self.pk])

    # def iterations(self):
    #     res = []
    #     if not self.cycles:
    #         return res
    #     for cs in self.cycles.split(';'):
    #         res.append(Iteration(s=cs).cycle())
    #     return res

    # def __init__(self, order_id=0, s="", cycle={}):
    #
    #     if s:
    #         x = s.split(':')
    #         #for sp in x[0].split(','):
    #             #p = Part()
    #             #p.name = sp
    #             #self.parts.add(p) # todo можно проверить принадлежность модели-item
    #         self.parts = x[0]
    #         self.mats = x[1]
    #     elif cycle:   # by cycle ### cycle = {'parts': [], 'mats': [], 'ids': {}, 'pids': {}}
    #         self.parts = ','.join(cycle['parts'])
    #         #for p in cycle['parts']:
    #             #self.parts.add(Part.Objects.get(name=p))
    #         self.mats = ""
    #         for m in cycle['mats']:
    #             if self.mats:
    #                 self.mats += ','
    #             self.mats += m
    #             ids = []
    #             if m in cycle['pids']:
    #                 ids += [f'p{id}' for id in cycle['pids'][m]]
    #             if m in cycle['ids']:
    #                 ids += [f'{id}' for id in cycle['ids'][m]]
    #             if ids:
    #                 self.mats += f"[{' '.join(ids)}]"
    #     else:
    #         self.parts = ""
    #         self.mats = ""
    #     #self.order = Order.objects.get(pk=order_id)
    #
    # def __str__(self):
    #     return f"{self.parts}:{self.mats}"
    #
    # def volume(self):
    #     return self.cycle()['N']
    #
    # def cycle(self):
    #     cycle = {'parts': [], 'mats': [], 'ids': {}, 'pids': {}, 'N': 0, "s": str(self)}
    #     if self.parts:
    #         cycle['parts'] = self.parts.split(",")
    #     for m in self.mats.split(','):
    #         if m[-1] == ']':  # need to get id. Let's parse string mat[id1,id2...]
    #             x = m[:-1].split('[')
    #             cycle['mats'].append(x[0])
    #             ids = x[1].split(' ')
    #             cycle['pids'][x[0]] = []
    #             cycle['ids'][x[0]] = []
    #             for id in ids:
    #                 if id[0] == 'p':
    #                     cycle['pids'][x[0]].append(id[1:])
    #                     cycle['N'] += Finish.objects.filter(pattern_id=int(id[1:])).count()
    #                 else:
    #                     cycle['ids'][x[0]].append(id)
    #                     cycle['N'] += 1
    #         else:
    #             cycle['N'] += Finish.objects.filter(pattern__nature__name=m).count()
    #             cycle['mats'].append(m)
    #
    #     return cycle



# class Shot(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     upload = models.FileField()


class Machine(models.Model):
    name = models.CharField(max_length=32)
    ip = models.GenericIPAddressField(null=True)
    working = models.BooleanField(null=True)  # null == unknown
    produced = models.PositiveIntegerField(default=0)
    power = models.FloatField(default=1)
    activeOrder = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    lastRender = models.DateTimeField(null=True)

    def render_made(self):
        self.produced += 1
        self.lastRender = make_aware(datetime.now())
        #self.activeOrder.renders_done += 1
        self.save()

    def __str__(self):
        return self.name

def validate_cycles(value):
    pass
#     if len(value) == 0:
#         raise ValidationError(
#             _('Invalid value: %(value)s'),
#             code='invalid',
#             params={'value': value},
#         )
