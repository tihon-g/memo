import os

from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand
from material.models import Finish, Nature, Pattern


class Command(BaseCommand):
	help = 'Search and add textures to db...'

	def handle(self, *args, **options):
		print("Start memo textures loading script...\n")
		APP = 'material'  # todo: взять имя приложения
		mats_dir = os.path.join(settings.BASE_DIR, APP, 'static', APP, 'textures')
		for path, dirs, txs in os.walk(mats_dir):  # walk through nested folder to find all textures of materials
			if path.split(os.sep)[-1]=='maps':
				continue  # need to skip maps folders
			rp = path[len(mats_dir)+1:]  # relative path
			mat_type = rp.split(os.sep)[0]
			for tx in txs:
				if tx == ".DS_Store":
					continue
				try:
					Finish.objects.get(url=tx)
				except Finish.DoesNotExist:
					try:  # choose type
						t = Nature.objects.get(name=mat_type)
					except Nature.DoesNotExist:
						t = Nature(name=mat_type)
						t.save()
						print("Add new material type: {}".format(t))
					try:  # choose pattern
						p = Pattern.objects.get(directory=rp)
					except Pattern.DoesNotExist:
						p = Pattern(name=mat_type, directory=rp, vendor='Memo Furniture', type_id=t.id)
						p.save()
						print("Add new material pattern: {}".format(p))
					if tx[-4:] == '.jpg':
						img = Image.open(os.path.join(path, tx)).convert('RGB')
						w, h = img.size
						dpi = img.info['dpi'][0]
						x = Finish(url=tx, pattern_id=p.id, w=w, h=h, dpi=dpi)
					else: # vrmat
						x = Finish(url=tx, pattern_id=p.id)
					x.save()
					print("Add texture {}".format(x))
		print("Done!")

