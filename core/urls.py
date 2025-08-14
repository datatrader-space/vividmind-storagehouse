from django.urls import path

from .views import file_upload_view
from django.urls import path, include

urlpatterns = [
    path("api/upload/", file_upload_view, name='file_upload_view'),
    
]