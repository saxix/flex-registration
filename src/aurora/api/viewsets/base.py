from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class SmartViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication, BasicAuthentication)
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
