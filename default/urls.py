from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upgrade/', views.upgrade, name='upgrade'),
    path('upload/', views.uploadfile, name='upload')
]
