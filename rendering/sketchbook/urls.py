from django.urls import path

from sketchbook.views import ProductsListView, ProductSketchbookView, ProductAPIView

app_name = 'sketchbook'

urlpatterns = [
    path('', ProductsListView.as_view(), name='index'),
    path('<int:pk>/', ProductSketchbookView.as_view()),
]

api_urlpatterns = [
    path('product/<int:pk>/', ProductAPIView.as_view()),
]
