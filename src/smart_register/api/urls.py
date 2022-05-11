from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import (
    FlexFormFieldViewSet,
    FlexFormViewSet,
    FormSetViewSet,
    RegistrationViewSet,
    UserViewSet,
    ValidatorViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register(r"user", UserViewSet)
router.register(r"registration", RegistrationViewSet)
router.register(r"form", FlexFormViewSet)
router.register(r"formset", FormSetViewSet)
router.register(r"field", FlexFormFieldViewSet)
router.register(r"validator", ValidatorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
