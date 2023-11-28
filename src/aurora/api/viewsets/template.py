from dbtemplates.models import Template

from rest_framework import serializers

from .base import SmartViewSet


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        exclude = ()


class TemplateViewSet(SmartViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
