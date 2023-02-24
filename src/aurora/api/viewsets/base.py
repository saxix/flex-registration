from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions


class LastModifiedFilter(filters.FilterSet):
    modified_after = filters.DateFilter(field_name="last_update_date", lookup_expr="gte")


class SmartViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication, BasicAuthentication)
    permission_classes = (IsAdminUser | DjangoModelPermissions,)
