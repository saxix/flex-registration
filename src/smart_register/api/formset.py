from rest_framework import serializers, viewsets

from smart_register.core.models import FormSet


class FormSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSet
        exclude = ()


class FormSetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = FormSet.objects.all()
    serializer_class = FormSetSerializer
