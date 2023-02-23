from django.contrib.flatpages.models import FlatPage
from rest_framework import serializers


class FlatPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatPage
        exclude = ()
