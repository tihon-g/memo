from django.urls import include, path
from django.views.generic import RedirectView

from . import views

# from django.contrib.auth.decorators import login_required
# @login_required

urlpatterns = [
    path('', views.index, name='homepage'),
    path('favicon.ico', RedirectView.as_view(url="/static/webapp/img/favicon.ico", permanent=True), name='favicon'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name="logout"),
    path('register/', views.regPage, name='register'),
    path('profile/', views.profile, name='profile'),
    path('social-auth/', include('social_django.urls', namespace="social")),
    path('api/', include([
        path('/', views.api_index, name='api'),
        path('models/', views.api_model_index, name='api-model-index'),
        path('products/',  include([
            path('', views.api_product_index, name='api-product-index'),
            path('<int:product_id>/', views.api_product_kinds, name='api-product-kinds'),
            path('<int:product_id>/<int:kind_id>', views.api_product_kind_details, name='api-product-kinds-details'),
        ])),
        path('patterns/', include([
            path('', views.api_pattern_index, name='api-pattern-index'),
            path('<int:pattern_id>/', views.api_pattern_details, name='api-pattern-details'),
        ])),
        path('finish/<int:finish_id>/', views.api_get_finish, name='api-get-finish'),
        path('qualities/', views.api_quality_index, name='api-qualities-index'),
        path('render/info/', views.api_render_info, name='api-render-info'),
        path('render/', views.api_get_render, name='api-render'),
        path('limitations', views.api_limitations, name='api-limitations'),
        path('colorcharts', views.api_colorcharts, name='api-colorcharts'),
        path('defaultfinish/<int:kind_id>', views.api_defaultfinish, name='api-defaultfinish'),

    ]))
]
