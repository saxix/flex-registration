import logging
import re
from datetime import datetime, timedelta

from django.contrib.admin import SimpleListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.urls import reverse
from django.utils.translation import gettext as _

from adminfilters.numbers import NumberFilter

from ...administration.filters import BaseAutoCompleteFilter

logger = logging.getLogger(__name__)


class OrganizationFilter(BaseAutoCompleteFilter):
    pass


#
# class LinkedAutoCompleteFilter(BaseAutoCompleteFilter):
#     parent = None
#     parent_lookup_kwarg = None
#     extras = []
#     dependants = []
#     def __init__(self, field, request, params, model, model_admin, field_path):
#         self.dependants = []
#         if self.parent:
#             self.parent_lookup_kwarg = f"{self.parent}__exact"
#         super().__init__(field, request, params, model, model_admin, field_path)
#         for pos, entry in enumerate(model_admin.list_filter):
#             if (
#                 len(entry) == 2
#                 and entry[0] != self.field_path
#                 and entry[1].__name__ == type(self).__name__
#                 and entry[1].parent == self.field_path
#             ):
#                 kwarg = f"{entry[0]}__exact"
#                 if entry[1].parent:
#                     if kwarg not in self.dependants:
#                         self.dependants.extend(entry[1].dependants)
#                         self.dependants.append(kwarg)
#
#
#     def has_output(self):
#         if self.parent:
#             return self.parent_lookup_kwarg in self.request.GET
#         return True
#
#     def choices(self, changelist):
#         to_remove = [self.lookup_kwarg, self.lookup_kwarg_isnull]
#         p = changelist.params.copy()
#         for f in p:
#             if f in self.dependants:
#                 to_remove.append(f)
#
#         self.query_string = changelist.get_query_string(remove=to_remove)
#         if self.lookup_val:
#             return [str(self.target_model.objects.get(pk=self.lookup_val)) or ""]
#         return []
#
#     def get_url(self):
#         url = reverse("%s:autocomplete" % self.admin_site.name)
#         if self.parent_lookup_kwarg in self.request.GET:
#             oid = self.request.GET[self.parent_lookup_kwarg]
#             return f"{url}?oid={oid}"
#         return url
#
#     @classmethod
#     def factory(cls, *, title=None, lookup_name="exact", **kwargs):
#         kwargs["filter_title"] = title
#         kwargs["lookup_name"] = lookup_name
#         return type("LinkedAutoCompleteFilter", (cls,), kwargs)
#


class RegistrationProjectFilter(BaseAutoCompleteFilter):
    fk_name = "project__organization__exact"

    def has_output(self):
        return "project__organization__exact" in self.request.GET

    def get_url(self):
        url = reverse("%s:autocomplete" % self.admin_site.name)
        if self.fk_name in self.request.GET:
            oid = self.request.GET[self.fk_name]
            return f"{url}?oid={oid}"
        return url


# class RegistrationFilter(BaseAutoCompleteFilter):
#     fk_name = "registration"
#
#     def has_output(self):
#         return "project__organization__exact" in self.request.GET
#
#     def get_url(self):
#         url = reverse("%s:autocomplete" % self.admin_site.name)
#         if self.fk_name in self.request.GET:
#             oid = self.request.GET[self.fk_name]
#             return f"{url}?oid={oid}"
#         return url


class HourFilter(SimpleListFilter):
    parameter_name = "hours"
    title = "Latest [n] hours"
    slots = (
        (30, _("30 min")),
        (60, _("1 hour")),
        (60 * 4, _("4 hour")),
        (60 * 6, _("6 hour")),
        (60 * 8, _("8 hour")),
        (60 * 12, _("12 hour")),
        (60 * 24, _("24 hour")),
    )

    def lookups(self, request, model_admin):
        return self.slots

    def queryset(self, request, queryset):
        if self.value():
            offset = datetime.now() - timedelta(minutes=int(self.value()))
            queryset = queryset.filter(timestamp__gte=offset)

        return queryset


class DateRangeFilter(NumberFilter):
    rex1 = re.compile(r"^(>=|<=|>|<|=)?(\d{4}-\d{2}-\d{2})$")
    re_range = re.compile(r"^(\d{4}-\d{2}-\d{2})..(\d{4}-\d{2}-\d{2})$")
    re_list = re.compile(r"(\d{4}-\d{2}-\d{2}),?")
    re_unlike = re.compile(r"^(<>)(?P<date>\d{4}-\d{2}-\d{2})$")

    def queryset(self, request, queryset):
        if self.value() and self.value()[0]:
            raw_value = self.value()[0]
            m1 = self.rex1.match(raw_value)
            m_range = self.re_range.match(raw_value)
            m_list = self.re_list.match(raw_value)
            m_unlike = self.re_unlike.match(raw_value)
            if m_unlike and m_unlike.groups():
                match = "%s__date__exact" % self.field.name
                op, value = self.re_unlike.match(raw_value).groups()
                queryset = queryset.exclude(**{match: value})
            else:
                if m1 and m1.groups():
                    op, value = self.rex1.match(raw_value).groups()
                    match = "%s__date__%s" % (self.field.name, self.map[op or "="])
                    self.filters = {match: value}
                elif m_range and m_range.groups():
                    start, end = self.re_range.match(raw_value).groups()
                    self.filters = {f"{self.field.name}__date__gte": start, f"{self.field.name}__date__lte": end}
                elif m_list and m_list.groups():
                    value = raw_value.split(",")
                    match = "%s__date__in" % self.field.name
                    self.filters = {match: value}
                # elif m_unlike and m_unlike.groups():
                #     match = '%s__exact' % self.field.name
                #     op, value = self.re_unlike.match(raw).groups()
                #     queryset = queryset.exclude(**{match: value})
                else:  # pragma: no cover
                    raise IncorrectLookupParameters()
                try:
                    queryset = queryset.filter(**self.filters)
                except Exception:
                    raise IncorrectLookupParameters(self.value())
        return queryset
