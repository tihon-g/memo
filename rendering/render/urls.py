from django.urls import path, include

from . import views

app_name = 'render'
urlpatterns = [
    path('', views.index, name='index'),
    path('kill_blender/<str:pids>/', views.kill_blender, name='kill_blender'),
    path('kill_queue/<str:pids>', views.killQueueManager, name='kill_queue'),
    path('start_queue/', views.startQueueManager, name='start_queue'),
    path('scene/', views.scene, name='scene'),
    path('scene/<int:scene_id>', views.scene_details, name='scene-details'),
    path('queue/', views.ajax_orderqueue, name='order-queue'),
    #path('activity/', views.ajax_activity, name='activity'),
    path('activity-scene/<int:scene_id>', views.activity_scene, name='activity-scene'),
    path('product/<int:product_id>/', include([
        #path('', views.product, name='product'),
        path('sketchbook/', views.productSketchbook, name='product-sketchbook'),
        path('renders/', views.ajax_get_all_product_renders, name='product-allrenders'),
        path('', views.productOrders, name='product-orders'),
    ])),
    path('order/', include([
        path('', views.ajaxCreateOrder, name='order-add'),
        path('<int:pk>/', include([
            path('', views.ajax_order_status, name='order-status'),
            # path('', views.orderEdit, name='order-edit'),
            path('sketchbook/', views.orderSketchbook, name='order-sketchbook'),
            path('renders/', views.ajax_get_all_order_renders, name='order-allrenders'),
            path('queue_up/', views.orderRun, name='order-run'),
            path('del/', views.orderDelete, name='order-delete'),
            path('cancel/', views.orderCancel, name='order-cancel'),
            path('stop/', views.orderStop, name='order-stop'),
            path('remove_data/', views.remove_order_data, name='order-remove-data'),
            path('post_data/<str:copy_type>', views.post_order_data, name='order-post-data'),
        ])),
    ])),
]
