from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from . import models


# from . import forms


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'kind', 'renders_done', 'N', 'quality', 'running', 'rule', 'worker')  # N  'shadow','volume'
    list_filter = (('kind', RelatedDropdownFilter), ('worker', RelatedDropdownFilter),)
    extra = 0


class ActorInline(admin.TabularInline):
    model = models.Actor

@admin.register(models.Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'world', )  # N
#    list_filter = (('kind', RelatedDropdownFilter), )
    extra = 0
    inlines = [ActorInline, ]


@admin.register(models.Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'orth', 'focus', 'phi', 'theta', 'r')  # N
#    list_filter = (('kind', RelatedDropdownFilter), )
    extra = 0
    fieldsets = (
            (None, {
                'fields': ('orth', 'focus', ('phi', 'theta', 'r'), ('lookAt_x','lookAt_y','lookAt_z'))
            }),
    )


@admin.register(models.Quality)
class QualityAdmin(admin.ModelAdmin):
    list_display = ('id', 'ext', 'engine', 'size_x', 'size_y', 'samples', 'compression')
    extra = 0

# not working -( disabled
# @admin.register(models.Order)
# class OrderAdmin(admin.ModelAdmin):
#     # for view list
#     list_display = ('id', 'model', 'cycles', 'renders_done', 'running',)
#     list_filter = (('model', RelatedDropdownFilter), )
#
#     # for edit any order or add order
#     form = forms.OrderForm
#     fieldsets = (
#         (None, {
#             'fields': ('model', 'cycles', )
#         }),
#         ('Scene options', {
#             'classes': ('expand',),
#             'fields': ('focus', 'angle_0', 'angle_3',),
#         }),
#         ('Advanced options - choose size', {
#             'classes': ('collapse',),
#             'fields': ('size_x', 'size_y', ),
#         }),
#         ('Admin (done) options', {
#             'classes': ('collapse',),
#             'fields': ('renders_done', 'N', 'running',	"created_by", "last_modified_by"),
#         }),
#     )
#
#


