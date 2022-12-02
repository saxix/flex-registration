from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class SmartViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
