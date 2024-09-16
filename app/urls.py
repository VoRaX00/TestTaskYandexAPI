from django.urls import path
from app import views

urlpatterns = [
    path('view-files', views.view_files, name='view_files'),
    path('download-file', views.download_file, name='download_file')
]