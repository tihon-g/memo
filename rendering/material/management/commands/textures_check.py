import os

from django.conf import settings
from django.core.management.base import BaseCommand
from material.models import Finish


class Command(BaseCommand):
	help = 'check how db and disk matches each other'

	# параметры -fix (не только проверить но и исправить)
	# -fix db ( исправить базу по диску)
	# -fix disk ( исправить диск по базе)

	def handle(self, *args, **options):
		print("Start check textures  script...\n")
		app_textures_dir = os.path.join(settings.BASE_DIR, 'material', 'static', 'material', 'textures')
		db_textures = [t.url for t in Finish.objects.all()]
		disk_dict = {}
		for path, dirs, txs in os.walk(app_textures_dir):  # walk through nested folder to find all textures of materials
			if path.split(os.sep)[-1] == 'maps':
				continue  # need to skip maps folders
			rp = path[len(app_textures_dir)+1:]  # relative path must be
			m_type = rp.split(os.sep)[0]
			m_pattern = rp[len(m_type)+1:] # empty for all mats except fabric
			for tx in txs:
				if tx[0] == '.':
					continue
				# 1. check in db
				try:
					t = Finish.objects.get(url=tx)
				except Finish.DoesNotExist:
					print("!! we have to add {} / {} to db or delete it from disk".format(rp, tx))
					continue  # next file
				# 2. check dublicate on disk
				if tx in disk_dict:
					disk_dict[tx] += 1
					print("dublicate {} / {}".format(rp, tx))
				else:
					disk_dict[tx] = 1
				# 3. check pattern
				p = t.pattern
				if p.directory != rp.replace('\\', '/'):
					print("!! texture {} has pattern dir conflict db:\n{} disk: \n{}".format(tx, p.directory, rp))
				# 4. check type
				if p.type.name != m_type:
					print(
						"!! texture {} has type conflict db:{} disk: {}".format(tx, p.type.name, m_type))
				# 5. vrmat must be in type dir
				if m_pattern == "":
					if tx.split(".")[-1] != 'vrmat':
						print("Textures in types dirs must be vrmat. what about {}?".format(rp))
				# 6.проверить что вся база есть на диске
				db_textures.remove(t.url)

				# todo:	# 6. check swatches

				# 7. projects static dir checked by staticback command


		print("{} textures only in db: {} ".format (len(db_textures), db_textures))
		print("Done!")

