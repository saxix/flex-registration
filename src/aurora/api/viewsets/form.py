from rest_framework import serializers
from strategy_field.utils import fqn

from aurora.core.models import FlexForm

from .base import SmartViewSet


class FormSerializer(serializers.ModelSerializer):
    base_type = serializers.CharField()
    # fields = serializers.StringRelatedField(many=True)
    # fields = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name'
    # )
    fields = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name="flexformfield-detail")

    class Meta:
        model = FlexForm
        exclude = ()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["base_type"] = fqn(instance.base_type)
        return data


class FlexFormViewSet(SmartViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = FlexForm.objects.all()
    serializer_class = FormSerializer
