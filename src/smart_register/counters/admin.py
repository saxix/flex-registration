import logging
from datetime import datetime

from admin_extra_buttons.decorators import button, view
from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib.admin import register
from django.db.transaction import atomic
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from smart_admin.modeladmin import SmartModelAdmin

from ..core.utils import is_root
from ..registration.admin import last_day_of_month
from .forms import ChartForm
from .models import Counter

logger = logging.getLogger(__name__)


@register(Counter)
class CounterAdmin(SmartModelAdmin):
    list_display = ("registration", "day", "records")
    list_filter = (("registration", AutoCompleteFilter), "day")
    date_hierarchy = "day"
    autocomplete_fields = ("registration",)
    change_form_template = None

    def get_exclude(self, request, obj=None):
        return ("details",)

    def get_readonly_fields(self, request, obj=None):
        if is_root(request):
            return []
        return ("registration", "day", "records")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return is_root(request)

    @view()
    def data(self, request, registration):
        qs = Counter.objects.filter(registration_id=registration).order_by("day")
        param_month = request.GET.get("m", None)
        total = 0
        if param_month:
            date = datetime.strptime(param_month, "%Y-%m-%d")
        else:
            date = timezone.now()

        qs = qs.filter(day__month=date.month)
        last_day = last_day_of_month(date)
        days = list(range(1, 1 + last_day.day))
        labels = [last_day.replace(day=d).strftime("%-d, %a") for d in days]
        values = {}
        for d in range(1, last_day.day + 1):
            dt = date.replace(day=d).date()
            values[dt] = {"total": 0, "pk": 0}
        for record in qs.all():
            values[record.day] = {"total": record.records, "pk": record.pk}
            total += record.records

        if not labels:
            labels = [d.strftime("%-d, %a") for d in values.keys()]

        data = {
            "datapoints": qs.all().count(),
            "label": date.strftime("%B %Y"),
            "day": date.strftime("%Y-%m-%d"),
            "total": total,
            "labels": labels,
            "data": list(values.values()),
        }

        response = JsonResponse(data)
        response["Cache-Control"] = "max-age=5"
        return response

    @button()
    def chart(self, request):
        ctx = self.get_common_context(request)
        if request.method == "POST":
            form = ChartForm(request.POST)
            if form.is_valid():
                registration = form.cleaned_data["registration"]
                ctx["title"] = registration.title
                ctx["registration"] = registration
        else:
            form = ChartForm()
        ctx["form"] = form
        return render(request, "admin/counters/counter/chart.html", ctx)

    @button()
    def collect(self, request):
        try:
            with atomic():
                result = Counter.objects.collect()
                self.message_user(request, str(result))
        except Exception as e:
            logger.exception(e)
            self.message_error_to_user(request, e)
