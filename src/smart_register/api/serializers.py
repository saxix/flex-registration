from rest_framework import serializers

from smart_register.registration.models import Record, Registration


class RegistrationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Registration
        fields = ["name", "title", "start", "end", "active", "locale"]


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Record
        fields = ["registration", "timestamp", "storage", "ignored"]
