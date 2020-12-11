import os

from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.safestring import mark_safe


class Nature(models.Model):
    """
    class represented a textures nature - fabric, wood, metal...
    """
    name = models.CharField(max_length=32)

    @property
    def patterns(self):
        return Pattern.objects.filter(nature_id=self.pk)

    @property
    def finishes(self):
        return Finish.objects.filter(pattern__nature_id=self.pk).exclude(archive=True)

    def __str__(self):
        return self.name


class Tile(models.Model):
    name = models.CharField(null=True, blank=True, max_length=32)
    w = models.PositiveIntegerField(null=True, blank=True)
    h = models.PositiveIntegerField(null=True, blank=True)
    dpi = models.FloatField(null=True, blank=True)
    multiplier = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}: {self.multiplier}x"

class HSV(models.Model):
    name = models.CharField(null=True, blank=True, max_length=32)
    hue = models.FloatField(null=True, blank=True)
    saturation = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"HSV={self.hue}/{self.saturation}/{self.value}"

class Features(models.Model):
    name = models.CharField(null=True, blank=True, max_length=32)
    color = models.CharField(null=True, verbose_name=(u'Color'), max_length=7, help_text=(u'HEX color, as #RRGGBB'), blank=True)
    roughness = models.FloatField(null=True, blank=True)
    specular = models.FloatField(null=True, blank=True)
    metalness = models.FloatField(null=True, blank=True)
    transparency = models.FloatField(null=True, blank=True)
    diffuse_hsv = models.ForeignKey(HSV, on_delete=models.PROTECT, null=True, blank=True)
    normalStrength = models.FloatField(null=True, blank=True)

    def __str__(self):
        hsv = self.diffuse_hsv if self.diffuse_hsv else "default"
        return f"{self.name}: roughness={self.roughness}, metalness={self.metalness}, normalstrength = {self.normalStrength}, hsv={hsv} "


class Maps(models.Model):
    name = models.CharField(null=True, max_length=32)
    diffuse =   models.CharField(choices=[('finish', 'finish'), ('pattern', 'pattern')], max_length=7, null=True, blank=True)
    roughness = models.CharField(choices=[('finish', 'finish'), ('pattern', 'pattern')], max_length=7, null=True, blank=True)
    specular =  models.CharField(choices=[('finish', 'finish'), ('pattern', 'pattern')], max_length=7, null=True, blank=True)
    normal =    models.CharField(choices=[('finish', 'finish'), ('pattern', 'pattern')], max_length=7, null=True, blank=True)

    def __str__(self):
        return self.name

class Pattern(models.Model):
    """
    class represented a Pattern - group of finishes
    """
    name = models.CharField(max_length=64, unique=True)
    directory = models.CharField(max_length=256)
    vendor = models.CharField(max_length=64, null=True, blank=True)
    nature = models.ForeignKey(Nature, on_delete=models.CASCADE)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE, null=True, blank=True)
    maps = models.ForeignKey(Maps, on_delete=models.CASCADE, null=True, blank=True)
    features = models.ForeignKey(Features, on_delete=models.PROTECT, null=True, blank=True)
    design = models.CharField(max_length=32, null=True, blank=True)
    squ = models.CharField(max_length=16, null=True, blank=True)
    web = models.URLField(max_length=128, null=True, blank=True)
    by = models.CharField(max_length=32, null=True, blank=True)
    copyrights = models.CharField(max_length=32, null=True, blank=True)

    @property
    def finishes(self):
        return Finish.objects.filter(pattern_id=self.pk).exclude(archive=True)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        #return reverse('material.views.pattern_details', args=[self.pk])
        return mark_safe(u'<a href="/material/pattern/{}">{}</a>'.format(self.pk, self.name))

    def url(self):
        return mark_safe(u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.format("/static/material/swatches/swatch_p{}.jpg".format(self.pk)))

    def swatch_src(self):
        return os.path.join(settings.STATIC_URL, 'material', 'swatches', f'swatch_p{self.id}.jpg')

    def swatch_link(self):
        return mark_safe(u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.format("/static/material/swatches/swatch_p{}.jpg".format(self.pk)))

    @property
    def diffuse(self):
        psqu = self.squ if self.squ else ''
        if self.maps:
            if self.maps.diffuse == 'pattern':
                return os.path.join(f'{self.name}_{psqu}.jpg')
        return ""

    @property
    def normal(self):
        psqu = self.squ if self.squ else ''
        if self.maps:
            if self.maps.normal == 'pattern':
                jpg = f'{self.name}_{psqu}_normal.jpg'
                png = f'{self.name}_{psqu}_normal.png'
                return png if os.path.exists(png) else jpg
        return ""
    # normal strength value in features

    @property
    def roughness(self):
        psqu = self.squ if self.squ else ''
        if self.maps:
            if self.maps.roughness == 'pattern':
                jpg = f'{self.name}_{psqu}_roughness.jpg'
                png = f'{self.name}_{psqu}_roughness.png'
                return png if os.path.exists(png) else jpg
        return ""
        # roughness value in features


class Finish(models.Model):
    """
    class represented a finish
    """
    name = models.CharField(null=True, blank=True, max_length=32)
    squ = models.CharField(max_length=16, null=True, blank=True)
    pattern = models.ForeignKey(Pattern, on_delete=models.PROTECT)
    tile = models.ForeignKey(Tile, on_delete=models.PROTECT, null=True, blank=True)
    #maps = models.ForeignKey(Maps, on_delete=models.CASCADE, null=True, blank=True)
    features = models.ForeignKey(Features, on_delete=models.PROTECT, null=True, blank=True)
    # textures does not uploaded in web. only put inside static and write paths below
    url = models.CharField(max_length=96, null=True, blank=True)  #diffuse
    #ordinal = models.PositiveIntegerField(null=True, blank=True)
    archive = models.BooleanField(default=False)

    @property
    def diffuse(self):
        psqu = self.pattern.squ if self.pattern.squ else ''
        if self.pattern.maps.diffuse == 'finish':
            return os.path.join(f'{self.pattern.name}_{psqu}_{self.squ}.jpg')
        elif self.pattern.maps.diffuse == 'pattern':
            return self.pattern.diffuse
        else:
            return ""

    @property
    def normal(self):
        psqu = self.pattern.squ if self.pattern.squ else ''
        if self.pattern.maps:
            if self.pattern.maps.normal == 'finish':
                return os.path.join(f'{self.pattern.name}_{psqu}_{self.squ}_normal.jpg')
            elif self.pattern.maps.normal == 'pattern':
                return self.pattern.normal
        return ""

    @property
    def roughness(self):
        psqu = self.pattern.squ if self.pattern.squ else ''
        if self.pattern.maps:
            if self.pattern.maps.roughness == 'finish':
                return os.path.join(f'{self.pattern.name}_{psqu}_{self.squ}_roughness.jpg')
            elif self.pattern.maps.roughness == 'pattern':
                return self.pattern.roughness
        return ""
        # roughness value in features

    @property
    def diffuse_relpath(self):
        return f"material/finishes/{self.pattern_id}/{self.diffuse}"

    def get_absolute_url(self):
        return mark_safe(u'<a href="static/{}">{}:{}</a>'.format(self.diffuse_relpath, self.squ, self.name))


    # now I prefer store swatches in static files. not in db
    def swatch_link(self): ## swatch
        return mark_safe(u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.
                         format(f"/static/material/swatches/swatch_{self.pk}.jpg"))

    swatch_link.short_description = "swatch"

    def image_link(self): ## swatch
        return mark_safe(u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.
                             format(f"/static/{self.diffuse_relpath}"))


    def pattern_link(self):
        return self.pattern.get_absolute_url()
        #mark_safe(u'<a href="/material/pattern/{}">{}</a>'.format(self.pattern.pk, self.pattern.name))

    pattern_link.allow_tags = True
    pattern_link.short_description = "pattern"

    ## todo get_absolute_url сделать и убрать харкод из html

    def __str__(self):
        if self.name:
            return f"[{self.id}] {self.name}"
        else:
            return f"[{self.id}] {self.pattern.name}:{self.squ}"

    #return f"[{self.id}] {self.url.replace('_tile.jpg','')}"


class ColorMatchingChart(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)

    def __str__(self):
        return self.name

    def match(self, suited):
        res = []
        for cm in ColorMatch.objects.filter(chart=self.pk):
            if str(suited) in cm.suited.split(','):
                res.append(cm.finish)
        return res


class ColorMatch(models.Model):
    chart = models.ForeignKey(ColorMatchingChart, on_delete=models.CASCADE, null=False)
    suited = models.CharField(validators=[validate_comma_separated_integer_list], max_length=2048, null=False)
    finish = models.ForeignKey(Finish, on_delete=models.PROTECT, blank=False, null=True)

    def __str__(self):
        return (f'use {self.finish.id} if before use one of {self.suited}')

# class Type(models.Model):
#     def finishes(self):
#         return Finish.objects.filter(pattern__nature_id=self.pk).exclude(archive=True)