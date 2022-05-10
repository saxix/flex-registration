from django.urls import path

from .views import editor_info

urlpatterns = [
    path("editor_info/", editor_info, name="editor_info"),
]
