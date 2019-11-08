from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('upload/', views.uploadfile, name='upload'),
    path('result/<str:folder>/<uuid:id>/', views.retrieve_result, name='retrieve_result'),
    path('result/<str:folder>/<uuid:id>/<str:format>/', views.retrieve_result, name='retrieve_result'),
    path('upgrade/', views.upgrade, name='upgrade'),
    path('upgrade/go/', views.perform_upgrade, name='perform_upgrade'),
    path('package-releases/', views.package_releases, name='package_releases'),
    path('package-releases/go/', views.perform_package_releases, name='perform_package_releases'),
    path('combine-packages/', views.combine_packages, name='combine_packages'),
    path('combine-packages/go/', views.perform_combine_packages, name='perform_combine_packages'),
    path('compile/', views.compile, name='compile'),
    path('compile/go/', views.perform_compile, name='perform_compile'),
    path('mapping-sheet/', views.mapping_sheet, name='mapping_sheet'),
    path('to-spreadsheet/', views.to_spreadsheet, name='to_spreadsheet'),
    path('to-spreadsheet/go/', views.perform_to_spreadsheet, name='perform_to_spreadsheet')
]
