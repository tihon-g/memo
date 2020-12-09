import os

from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand
from material.models import Finish, Pattern


class Command(BaseCommand):
	help = 'check & create swatches for material (not for furniture)'

	def handle(self, *args, **options):
		print("Start check & create swatches script...\n")
		APP = 'material'
		mats_dir = os.path.join(settings.BASE_DIR, APP, 'static', APP)
		textures_dir = os.path.join(mats_dir, 'textures')
		swatches_dir = os.path.join(mats_dir, 'swatches')
		R = {'w': settings.MATERIAL_SWATCH_INCHSIZE[0] * settings.MATERIAL_SWATCH_DPI,
			 'h': settings.MATERIAL_SWATCH_INCHSIZE[1] * settings.MATERIAL_SWATCH_DPI}
		# textures swatches
		for t in Finish.objects.all():
			swatch = os.path.join(swatches_dir,"swatch_{}.jpg".format(t.id))
			if os.path.exists(swatch):
				continue
			print("swatch for {} missed! Now we create it!".format(t.url), end="...")
			url = t.url.split('.')
			if url[-1] == 'vrmat':
				jpg = os.path.join(textures_dir, t.pattern.directory, "maps", "{} diffuse.jpg".format(url[0]))
				print("diffuse", end="...")
			else:  # jpg
				jpg = os.path.join(textures_dir, t.pattern.directory, t.url)
			if not os.path.exists(jpg):
				print("jpg {} file missed too!!!".format(jpg))
				continue
			try:
				tile = Image.open(jpg)
				dpi = tile.info['dpi'][0]
				if dpi != t.dpi and  t.url.split('.')[-1] != 'vrmat':
					print("incorrect dpi in db - Must fix!")
				k = settings.MATERIAL_SWATCH_DPI / dpi # we can use data from file but use it from db
				ctile_size = [int(x * k) for x in tile.size]
				ctile = tile.resize(ctile_size) # size of tile
				if ctile_size[0] >= R['w'] and ctile_size[1] >= R['h']:  # ctile larger than need -> crop
					res = ctile.crop((0, 0, R['w'], R['h']))
				else:  # ctile smaller than need -> dublicate
					res = Image.new(mode='RGB', size=(R['w'], R['h']))  # canvas
					for x in range(1 + (R['w'] - 1) // ctile_size[0]):
						for y in range(1 + (R['h'] - 1) // ctile_size[1]):
							res.paste(ctile, (x * ctile_size[0], y * ctile_size[1])) # multi paste original image
				res.save(swatch, quality=90, progressive=True, optimize=True)
				print("OK")
			except:
				print("but jpg texture could not open!")
		# pattern swatches
		GAP = 8
		for p in Pattern.objects.all():
			pswatch = os.path.join(swatches_dir, "swatch_p{}.jpg".format(p.id))
			if os.path.exists(pswatch):
				continue
			print("Pattern swatch for {} missed! Now we create it!".format(p.name), end="...")
			tiles = []
			try:
				res = Image.new(mode='RGB', size=(2 * R['w'] + GAP, 2 * R['h'] + GAP)) # canvas
				for t in Finish.objects.filter(pattern=p)[:4]:
					tiles.append(Image.open(os.path.join(swatches_dir, "swatch_{}.jpg".format(t.id))))
				if len(tiles) == 4:
					for k in range(4):  # combine
						res.paste(tiles[k], ((k%2) * (R['w']+GAP), (k//2) * (R['h']+GAP)))
					res.save(pswatch, quality=90, progressive=True, optimize=True)
					print("OK")
				else:
					print("failed")
			except Exception as e:
				print("but error {} occured!!!".format(e))
		print ("Done!")
