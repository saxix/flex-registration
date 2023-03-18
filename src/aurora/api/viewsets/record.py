from django_filters import rest_framework as filters

from ...registration.models import Record
from ..serializers import RecordSerializer
from .base import SmartViewSet


class RecordFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name="id", lookup_expr="gte")
    after = filters.DateFilter(field_name="timestamp", lookup_expr="gte")

    class Meta:
        model = Record
        fields = ["registration", "after", "id"]


class RecordViewSet(SmartViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filterset_class = RecordFilter

    # class Meta:
    #     datatables_extra_json = ("fields", )
    #
    #
    # def get_fields(self):
    #     return "fields", {
    #         "artist": [{'label': obj.name, 'value': obj.pk} for obj in Artist.objects.all()],
    #         "genre": [{'label': obj.name, 'value': obj.pk} for obj in Genre.objects.all()]
    #     }
