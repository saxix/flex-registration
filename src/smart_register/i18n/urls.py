from django.urls import path

from .views import editor_info, SmartJavascriptCatalog

urlpatterns = [
    path("editor_info/", editor_info, name="editor_info"),
    path("<str:locale>/", SmartJavascriptCatalog.as_view(), name="javascript-catalog"),
]
