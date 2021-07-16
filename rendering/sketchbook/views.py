from django.db.models import Q
from django.views.generic import ListView, TemplateView
from rest_framework.generics import RetrieveAPIView

from furniture.models import Product
from sketchbook.serializers import ProductSerializer


class ProductsListView(ListView):
    queryset = Product.objects.filter(~Q(type='toy')).order_by('sort_order') #.order_by('collection')
    template_name = 'sketchbook/products_list.html'


class ProductSketchbookView(TemplateView):
    template_name = 'sketchbook/product_sketchbook.html'


class ProductAPIView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
