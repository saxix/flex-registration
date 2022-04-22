from django.urls import include, path
from rest_framework.routers import DefaultRouter

from smart_register.api.field import FlexFormFieldViewSet

# Create a router and register our viewsets with it.
from smart_register.api.form import FlexFormViewSet
from smart_register.api.formset import FormSetViewSet
from smart_register.api.registration import RegistrationViewSet
from smart_register.api.validator import ValidatorViewSet

router = DefaultRouter()
router.register(r"registration", RegistrationViewSet)
router.register(r"form", FlexFormViewSet)
router.register(r"formset", FormSetViewSet)
router.register(r"field", FlexFormFieldViewSet)
router.register(r"validator", ValidatorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
