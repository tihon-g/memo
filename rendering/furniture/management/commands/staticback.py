import os
from django.core.management.base import BaseCommand
from django.conf import settings
import shutil

class Command(BaseCommand):
    help = 'check how collect static files '

    def add_arguments(self, parser):
        parser.add_argument('do', nargs=1, type=int, default=False)

    def handle(self, *args, **options):
        print("Start collect static back script...\n")
        do = (options['do'][0] == 1)
        for st_dir in settings.STATICFILES_DIRS:
            #print(st_dir)
            for path, dirs, files in os.walk(st_dir):
                for f in files:
                    if f[0] == '.':
                        continue
                    f2 = os.path.join(path.replace(st_dir, settings.STATIC_ROOT), f)
                    if not os.path.exists(f2):
                        print("need to call collect static! for file '{}'->{}".format(f,f2))

        for path, dirs, files in os.walk(settings.STATIC_ROOT):
            rp = path[len(settings.STATIC_ROOT) + 1:]
            for f in files:
                if f[0] == '.' or '_embedded_files' in rp:
                    continue
                app = rp.split(os.sep)[0]
                app_staticdir = os.path.join(settings.BASE_DIR, app, 'static')
                if app_staticdir in settings.STATICFILES_DIRS:
                    f2 = os.path.join(app_staticdir, rp)
                    if not os.path.exists(f2):
                        print("save new static file {}+{} to static app {} folder ".format(rp,f,app))
                        if do:
                            shutil.copy(f, f2)
        print("Done!")

