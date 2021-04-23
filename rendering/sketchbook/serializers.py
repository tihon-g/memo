from django.db.models import Q
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, ListSerializer

from furniture.models import Part, Configuration, Product, ProductKind, Limitation
from material.models import Nature, Finish


class FinishSerializer(ModelSerializer):
    url = SerializerMethodField()

    def get_url(self, obj):
        return f'/static/material/swatches/swatch_{obj.id}.jpg'

    class Meta:
        model = Finish
        fields = '__all__'


class NatureSerializer(ModelSerializer):
    finishes = SerializerMethodField(method_name='get_limited_by_configuration_finishes')

    def get_limited_by_configuration_finishes(self, obj):
        if 'configuration' in self.root.context:
            limitation = self.root.context['configuration'].limitation

            if limitation:
                qs = obj.finishes.filter(Q(pattern__in=limitation.patterns.all()) |
                                         Q(id__in=limitation.finishes.values_list('id', flat=True)))
                return FinishSerializer(qs, many=True).data

        return FinishSerializer(obj.finishes.all(), many=True).data

    class Meta:
        model = Nature
        fields = ['id', 'name', 'finishes']


class LimitationSerializer(ModelSerializer):
    class Meta:
        model = Limitation
        fields = '__all__'


class ProductPartSerializer(ModelSerializer):
    natures = NatureSerializer(many=True)
    meshes = SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = Part
        fields = '__all__'


class ConfigurationSerializer(ModelSerializer):
    part = SerializerMethodField()
    limitation = LimitationSerializer()

    def get_part(self, configuration):
        return ProductPartSerializer(instance=configuration.part,
                                     context={'configuration': configuration}).data

    class Meta:
        model = Configuration
        fields = '__all__'


class ProductKindSerializer(ModelSerializer):
    configuration_set = ConfigurationSerializer(many=True)

    class Meta:
        model = ProductKind
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    productkind_set = ProductKindSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'
