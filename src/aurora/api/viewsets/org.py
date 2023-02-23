from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from ...core.models import Organization, Project
from ..serializers import OrganizationSerializer, ProjectSerializer
from .base import LastModifiedFilter, SmartViewSet


class OrganizationViewSet(SmartViewSet):
    queryset = Organization.objects.order_by("lft")
    serializer_class = OrganizationSerializer
    # lookup_field = "slug"
    # LastModifiedFilter
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ('last_update_date',)
    filterset_class = LastModifiedFilter

    @action(detail=True, methods=["GET"])
    def projects(self, request, pk=None):
        # item = Organization.objects.get(slug=slug)
        queryset = Project.objects.filter(organization__id=pk)
        page = self.paginate_queryset(queryset)

        serializer = ProjectSerializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response
        # return Response(serializer.data, status=status.HTTP_200_OK)
