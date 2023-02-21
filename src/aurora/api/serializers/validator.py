from rest_framework import serializers

from aurora.core.models import Validator


class ValidatorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Validator
        exclude = ()
        lookup_field = "name"
        extra_kwargs = {"url": {"lookup_field": "name"}}