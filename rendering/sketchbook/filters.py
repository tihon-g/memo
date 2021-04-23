from django_filters import rest_framework as filters

from furniture.models import Part, Product, Configuration, ProductKind


class ConfigurationFilter(filters.FilterSet):
    product_kind_id = filters.ModelChoiceFilter(
        queryset=ProductKind.objects.all(),
        field_name='kind'
    )

    class Meta:
        model = Configuration
        fields = ['product_kind_id']


class ProductPartsFilter(filters.FilterSet):
    product_id = filters.ModelChoiceFilter(
        queryset=Product.objects.all(),
        field_name='configuration__kind__product'
    )

    class Meta:
        model = Part
        fields = ['product_id']
