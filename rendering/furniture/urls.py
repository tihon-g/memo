"""rendering URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from . import views

app_name = 'furniture'
urlpatterns = [
                path('', views.index, name='index'),
                path('collection/<str:selected_collection>', views.index, name='collection'),
                path('<int:product_id>', views.product_details, name='details'),
                path('<int:product_id>/addmeshes/<str:json_meshes>', views.add_meshes, name='add-meshes'),
              ]
