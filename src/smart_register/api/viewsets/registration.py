from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from smart_register.registration.models import Registration

from .base import SmartViewSet


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        exclude = ()


class RegistrationViewSet(SmartViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    lookup_field = "slug"

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    @action(detail=True, permission_classes=[AllowAny], authentication_classes=[])
    def version(self, request, slug=None):
        reg = self.get_object()
        return Response({"version": reg.version})
