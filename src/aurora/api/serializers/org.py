from rest_framework import serializers
from rest_framework.reverse import reverse

from ...core.models import Organization


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    projects = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        exclude = ("lft", "rght", "tree_id", "level")
        # fields = ("url", "name", "slug", "parent", "registrations")
        # lookup_field = "slug"
        # extra_kwargs = {
        #     'url': {'lookup_field': 'slug'}
        # }

    def get_projects(self, obj):
        req = self.context["request"]
        return req.build_absolute_uri(reverse("api:organization-projects", kwargs={"pk": obj.pk}))
