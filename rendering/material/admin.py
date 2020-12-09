from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter  # ,ChoiceDropdownFilter

from .models import Nature, Finish, Pattern, ColorMatchingChart, ColorMatch, Features, Maps, Tile, HSV


class ColorMatchInline(admin.TabularInline):
    model = ColorMatch
    extra = 0

class TextureInline(admin.TabularInline):
    model = Finish
    extra = 0

class PatternInline(admin.TabularInline):
    model = Pattern
    extra = 0

@admin.register(Nature)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_links = ('id')
    inlines = [PatternInline, ]

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'squ', 'nature',)
        }),
        ('Author options', {
            'classes': ('collapse',),
            'fields': ('web', 'design', 'by', 'copyrights'),
        }),
        ('Admin options', {
            'classes': ('collapse',),
            'fields': ('maps', 'features', 'tile', ),
        }),
    )

    search_fields = ['name', ]
    list_display = ('name', 'vendor', 'nature', 'swatch_link')
    list_filter = (
        ('vendor', DropdownFilter),
        ('nature', RelatedDropdownFilter),
    )
    inlines = [TextureInline, ]

@admin.register(Finish)
class TextureAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('squ', 'pattern', 'archive', 'name')
        }),
        ('Admin options', {
            'classes': ('collapse',),
            'fields': ('features', 'tile', ),
        }),
    )

    list_display = ('id', 'name', 'squ', 'pattern_link', 'swatch_link', 'archive',)
    list_links = ('id', 'pattern_link', 'swatch_link', )
    list_filter = (
        ('archive', DropdownFilter),
        ('pattern', RelatedDropdownFilter),
    )

@admin.register(ColorMatchingChart)
class ColorMatchingChartAdmin(admin.ModelAdmin):
    inlines = [ColorMatchInline, ]
    list_display = ('id', 'name', )


@admin.register(Features)
class FeaturesAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in Features._meta.get_fields()]
    list_display = ('name', 'color', 'roughness', 'specular', 'metalness', 'transparency', 'normalStrength', 'diffuse_hsv')

@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in Tile._meta.get_fields()]
    list_display = ('name', 'w', 'h', 'dpi', 'multiplier')

@admin.register(Maps)
class MapsAdmin(admin.ModelAdmin):
    #list_display =[field.name for field in Maps._meta.get_fields()]
    list_display = ('name', 'diffuse', 'normal', 'specular')

@admin.register(HSV)
class HSVAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in HSV._meta.get_fields()]
    list_display = ('name', 'hue', 'saturation', 'value' )