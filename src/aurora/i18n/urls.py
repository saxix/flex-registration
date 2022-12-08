from django.urls import path

from .views import SmartJavascriptCatalog, editor_info, set_language

urlpatterns = [
    path("editor_info/", editor_info, name="editor_info"),
    path("<str:locale>/", SmartJavascriptCatalog.as_view(), name="javascript-catalog"),
    path("setlang/", set_language, name="set_language"),
]
