from rest_framework import viewsets, serializers

from smart_register.registration.models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        exclude = ()


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
