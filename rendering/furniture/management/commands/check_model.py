# -*- coding: utf-8 -*-


# it does not work
# todo repair it

import json
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from furniture.models import Model3D


# stdout
# When you are using management commands and wish to provide console output, you should write to self.stdout and self.stderr,
# instead of printing to stdout and stderr directly. By using these proxies, it becomes much easier to test your custom command.
# Note also that you don’t need to end messages with a newline character, it will be added automatically, unless you specify the ending parameter:

# todo Eсли хотите из одного процесса выходные данные передать на вход другого процесса, то можно так:
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


class Command(BaseCommand):
    help = 'check blender model'
    state = {}
    def add_arguments(self, parser):
        parser.add_argument('model', nargs=1, type=int, default=False)

    def handle(self, *args, **options):
        blend = Model3D.objects.get(pk=options['model'][0]).blend
        res = {'log': ''}
        if len(blend.path):
            cmd = []
            #cmd = settings.RENDER_MACHINE["RENDER_CMD_CHECK"]
            root = settings.BASE_DIR
            #cmd[1] = os.path.join(settings.BLENDER_MODELS_STORAGE, blend.path)
            for s in execute_wait(cmd):
                if 'meshes:' in s:  #json.dumps(meshes, indent=2)
                    res['meshes'] = json.loads(s[len('meshes:'):].rstrip('\n'))
                res['log'] += s
            return json.dumps(res['meshes'], indent=None, separators=(",", ":"))
        else:
            raise ValueError('no any blend file')
