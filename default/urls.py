from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.uploadfile, name='upload'),
    path('upgrade/', views.upgrade, name='upgrade'),
    path('upgrade/go/', views.perform_upgrade, name='perform_upgrade'),
    path('result/<str:folder>/<uuid:id>/', views.retrieve_result, name='retrieve_result')
]
