from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, ChoiceDropdownFilter, DropdownFilter

# from ajax_select.fields import AutoCompleteSelectMultipleField
# raw_id_fields
from . import models


# If you define the Meta.model attribute on a ModelForm, you must also define the Meta.fields attribute (or the Meta.exclude attribute).
# However, since the admin has its own way of defining fields, the Meta.fields attribute will be ignored.
#
# If the ModelForm is only going to be used for the admin, the easiest solution is to omit the Meta.model attribute, since ModelAdmin will provide the correct model to use.
# Alternatively, you can set fields = [] in the Meta class to satisfy the validation on the ModelForm.


######################  PartAdmin  #################################

@admin.register(models.Mesh)
class MeshAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'name')
    list_editable = ('name',)
    list_display_links = ('id',)
    extra = 0
    list_filter = (
        ('model', RelatedDropdownFilter),
    )

# 1. Model3D <- Mesh
# ###################### Model3DAdmin ################################
class MeshInline(admin.TabularInline):
    model = models.Mesh
    extra = 0

@admin.register(models.Model3D)
class Model3DAdmin(admin.ModelAdmin):
    #todo fix url to blend & glb
    list_display = ('id', 'name', 'blend', 'glb')  # 'added_by', 'last_modified_by'
    inlines = [MeshInline, ]
    list_display_links = ('id', )
    extra = 0
    exclude = ('last_modified_by',)

    # TODO Загруженную модель копировать в папку furniture и прописывать правильное имя в БД


#2. Product <- ProductKind <- Part <- cover, meshes
# ###################### ProductAdmin ################################
class ProductKindInline(admin.TabularInline):
    model = models.ProductKind
    extra = 0

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # fields = (('name', 'producer'), ('collection', 'type'), 'swatch')
    search_fields = ['name', ]
    extra = 0
    list_display = ('name', 'type', 'product_code', 'collection', 'swatch_link',)
    inlines = [ProductKindInline, ]
    list_filter = (
        ('collection', DropdownFilter),
        ('type', ChoiceDropdownFilter),
        ('producer', ChoiceDropdownFilter),
    )


# # ###################### ProductKindAdmin ################################
# class PartInline(admin.TabularInline):  # StackedInline
#     model = models.ProductKind.parts.through
#     #filter_vertical = ('meshes',)
#     extra = 0

class ConfigurationInline(admin.TabularInline):  # StackedInline
    model = models.ProductKind.parts.through
    #filter_vertical = ('meshes',)
    extra = 0


@admin.register(models.ProductKind)
class ProductKindAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    list_display = ('name', 'product', 'comment')  # ,  'renderOrderTemplate'
    list_display_links = ('name', 'product')  # https://stackoverflow.com/questions/3998786/change-list-display-link-in-django-admin
    inlines = [ConfigurationInline, ]
    # exclude = ('parts',)
    extra = 0
    list_filter = (
        ('product', RelatedDropdownFilter),
    )
    # def order(self, obj):
    #     return obj.renderOrder()
    #order.short_description = 'order'


@admin.register(models.Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    # fields = (('name', 'producer'), ('collection', 'type'), 'swatch')
    #search_fields = ['name', ]
    extra = 0
    list_display = ('id', 'kind', 'part', 'limitation', 'colorChart')
    list_filter = (
        ('kind', RelatedDropdownFilter),
        ('part', RelatedDropdownFilter),
    )




######################  PartAdmin  #################################
class CoveredPartInLine(admin.TabularInline):
    model = models.Part.cover.through
    extra = 1

class MeshesInLine(admin.TabularInline):
    model = models.Part.meshes.through
    extra = 1

# class LimitationInline(admin.TabularInline):  # StackedInline
#     model = models.Limitation
#     extra = 0

@admin.register(models.Part)
class PartAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    #exclude = ('meshes', 'cover',)
    list_display = ('id',  'name', 'displayName' ) # 'model'
    list_editable = ('name',)
    list_display_links = ('id',)

    #inlines = [CoveredPartInLine, MeshesInLine]
    filter_horizontal = ('meshes',)

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "meshes":
    #         kwargs["queryset"] = models.Mesh.objects.filter(model_id=18)
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)
    #
    # def link_to_kind(self, obj):
    #     link = reverse("admin:furniture_productkind_change", args=[obj.ProductKind.id])  # model name has to be lowercase
    #     return u'<a href="%s">%s</a>' % (link, obj.ProductKind.name)


@admin.register(models.Limitation)
class LimitationAdmin(admin.ModelAdmin):
    #list_display = ('part', )
    raw_id_fields = ('patterns', 'finishes',)
