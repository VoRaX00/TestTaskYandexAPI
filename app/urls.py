from django.urls import path
from app import views

app_name = 'app'

urlpatterns = [
    path('view-files', views.view_files, name='view-files'),
    path('download-file', views.download_file, name='download-file')
]