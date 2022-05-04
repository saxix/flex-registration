from rest_framework import viewsets, serializers

from smart_register.core.models import Validator


class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
        exclude = ()


class ValidatorViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = Validator.objects.all()
    serializer_class = ValidatorSerializer
