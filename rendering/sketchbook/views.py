from django.views.generic import ListView, TemplateView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from furniture.models import Product, Part, Configuration
from sketchbook.filters import ConfigurationFilter
from sketchbook.serializers import ConfigurationSerializer, ProductSerializer


class ProductsListView(ListView):
    queryset = Product.objects.all()
    template_name = 'sketchbook/products_list.html'


class ProductSketchbookView(TemplateView):
    template_name = 'sketchbook/product_sketchbook.html'


class ProductAPIView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ConfigurationsAPIView(ListAPIView):
    serializer_class = ConfigurationSerializer
    queryset = Configuration.objects.all()
    filterset_class = ConfigurationFilter
