from django.urls import path, include

from . import views

app_name = 'material'
urlpatterns = [
    path('', views.index, name='index'),
    path('selected_nature/<int:nature_id>', views.index, name='index_nature'),
    path('selected_pattern/<int:pattern_id>', views.index, name='index_pattern'),
    path('nature/<int:pk>/', views.index, name='nature-details'),
    path('pattern/<int:pk>/', views.pattern_details, name='pattern-details'),
    path('finish/<int:pk>/', views.finish_details, name='finish-details'),

    path('colorchart/', include([
        path('', views.colorchart_index, name='colorchart-index'),
        path('<int:pk>/', views.colorchart, name='colorchart'),
        ])),


]

