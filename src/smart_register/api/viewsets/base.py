from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class SmartViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
