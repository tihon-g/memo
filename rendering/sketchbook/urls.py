from django.urls import path

from sketchbook.views import ProductsListView, ProductSketchbookView, ConfigurationsAPIView, ProductAPIView

app_name = 'sketchbook'

urlpatterns = [
    path('', ProductsListView.as_view()),
    path('<int:pk>/', ProductSketchbookView.as_view()),
]

api_urlpatterns = [
    path('product/<int:pk>/', ProductAPIView.as_view()),
    path('configurations/', ConfigurationsAPIView.as_view()),
]
