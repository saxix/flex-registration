from django.urls import path

from .views import SmartJavascriptCatalog, editor_info

urlpatterns = [
    path("editor_info/", editor_info, name="editor_info"),
    path("<str:locale>/", SmartJavascriptCatalog.as_view(), name="javascript-catalog"),
]
