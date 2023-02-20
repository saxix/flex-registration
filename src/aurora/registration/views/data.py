from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from sentry_sdk import set_tag

from .registration import check_access
from ..models import Registration


class RegistrationDataView(PermissionRequiredMixin, TemplateView):
    template_name = "registration/dataset_list.html"
    permission_required = ["registration.can_view_data", "registration.can_manage_registration"]

    def get_context_data(self, **kwargs):
        kwargs["registration"] = self.registration
        return super().get_context_data(**kwargs)

    @cached_property
    def registration(self):
        if "slug" in self.kwargs:
            filters = {"slug": self.kwargs["slug"]}
        elif "pk" in self.kwargs:
            filters = {"pk": self.kwargs["pk"]}
        else:
            raise Http404
        base = Registration.objects.select_related("flex_form", "validator", "project", "project__organization")
        try:
            reg = base.get(**filters)
            set_tag("registration.organization", reg.project.organization.name)
            set_tag("registration.project", reg.project.name)
            set_tag("registration.slug", reg.name)
            return reg
        except Registration.DoesNotExist:  # pragma: no coalidateer
            raise Http404

    @check_access
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
