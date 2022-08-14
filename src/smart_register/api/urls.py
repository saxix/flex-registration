from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import (
    FlexFormFieldViewSet,
    FlexFormViewSet,
    FormSetViewSet,
    RegistrationViewSet,
    UserViewSet,
    TemplateViewSet,
    ValidatorViewSet,
    project_info,
    extract,
    load
)

app_name = "api"

router = DefaultRouter()
router.register(r"user", UserViewSet)
router.register(r"registration", RegistrationViewSet)
router.register(r"form", FlexFormViewSet)
router.register(r"formset", FormSetViewSet)
router.register(r"field", FlexFormFieldViewSet)
router.register(r"validator", ValidatorViewSet)
router.register(r"template", TemplateViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("project/", project_info),
    path("extract/<str:model>/<int:pk>/", extract),
    path("load/", load),
]
