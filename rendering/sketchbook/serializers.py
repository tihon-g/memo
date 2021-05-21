from django.db.models import Q
from rest_framework.fields import SerializerMethodField, ReadOnlyField, CharField
from rest_framework.serializers import ModelSerializer

from furniture.models import Part, Configuration, Product, ProductKind
from material.models import Nature, Finish, Pattern


class FinishSerializer(ModelSerializer):
    url = SerializerMethodField()
    display_name = CharField()

    def get_url(self, obj):
        return f'/static/material/swatches/swatch_{obj.id}.jpg'

    class Meta:
        model = Finish
        fields = ['id', 'url', 'display_name']


class PatternSerializer(ModelSerializer):
    finishes = SerializerMethodField(method_name='get_limited_finishes')

    def get_limited_finishes(self, obj):
        if 'configuration' in self.root.context:
            limitation = self.root.context['configuration'].limitation

            if limitation:
                filter_by_limitation = (
                        Q(pattern__in=limitation.patterns.all()) |
                        Q(id__in=limitation.finishes.values_list('id', flat=True))
                )

                qs = obj.finish_set.filter(filter_by_limitation, archive=False)
                return FinishSerializer(qs, many=True).data

        return FinishSerializer(obj.finish_set.filter(archive=False), many=True).data

    class Meta:
        model = Pattern
        fields = ['id', 'name', 'finishes']


class NatureSerializer(ModelSerializer):
    patterns = SerializerMethodField(method_name='get_limited_patterns')

    def get_limited_patterns(self, obj):
        if 'configuration' in self.root.context:
            limitation = self.root.context['configuration'].limitation

            if limitation:
                qs = obj.pattern_set.filter(id__in=limitation.patterns.values_list('id', flat=True))
                return PatternSerializer(qs, many=True).data

        return PatternSerializer(obj.pattern_set.all(), many=True).data

    class Meta:
        model = Nature
        fields = ['id', 'name', 'patterns']


class ProductPartSerializer(ModelSerializer):
    natures = NatureSerializer(source='cover', many=True)

    class Meta:
        model = Part
        fields = ['id', 'name', 'natures']


class ConfigurationSerializer(ModelSerializer):
    part = SerializerMethodField()
    removable = ReadOnlyField()

    def get_part(self, configuration):
        return ProductPartSerializer(instance=configuration.part,
                                     context={'configuration': configuration}).data

    class Meta:
        model = Configuration
        fields = ['id', 'part', 'limitation', 'removable', 'optional', 'defaultFinish', 'colorChart']


class ProductKindSerializer(ModelSerializer):
    configuration_set = ConfigurationSerializer(many=True)

    class Meta:
        model = ProductKind
        fields = ['id', 'name', 'configuration_set']


class ProductSerializer(ModelSerializer):
    productkind_set = ProductKindSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'productkind_set']
