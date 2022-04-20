import logging

from constance import config
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.decorators.http import condition
from django.views.generic import TemplateView

from smart_register.core.utils import get_qrcode, get_etag
from smart_register.registration.models import Registration

logger = logging.getLogger(__name__)


def error_csrf(request, reason=""):
    if reason:
        logger.error(reason)
    return TemplateResponse(request, "csrf.html", status=400)


def error_404(request, exception):
    return TemplateResponse(request, "404.html", status=404, headers={"Session-Token": settings.DJANGO_ADMIN_URL})


class PageView(TemplateView):
    template_name = "index.html"

    def get_template_names(self):
        return [f"{self.kwargs['page']}.html"]

    def get_context_data(self, **kwargs):
        from smart_register.i18n.gettext import gettext as _

        return super().get_context_data(title="Title", title2=_("Title2"), **kwargs)


@method_decorator(condition(etag_func=get_etag, last_modified_func=None), name="dispatch")
@method_decorator(cache_control(public=True), name="dispatch")
class HomeView(TemplateView):
    template_name = "ua.html"

    def get_context_data(self, **kwargs):
        selection = config.HOME_PAGE_REGISTRATIONS.split(";")
        buttons = []
        for slug in selection:
            if slug.strip():
                try:
                    buttons.append(Registration.objects.get(active=True, slug=slug.strip()))
                except Exception as e:
                    logger.exception(e)
        return super().get_context_data(buttons=buttons, **kwargs)


class QRCodeView(TemplateView):
    template_name = "qrcode.html"

    def get_context_data(self, **kwargs):
        url = self.request.build_absolute_uri("/")
        qrcode = get_qrcode(url)
        return super().get_context_data(**kwargs, qrcode=qrcode, url=url)


class ProbeView(View):
    http_method_names = ["get", "head"]

    def head(self, request, *args, **kwargs):
        return HttpResponse("Ok")

    def get(self, request, *args, **kwargs):
        return HttpResponse("Ok")


def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)


class MaintenanceView(TemplateView):
    template_name = "maintenance.html"

    def get(self, request, *args, **kwargs):
        if not config.MAINTENANCE_MODE:
            return HttpResponseRedirect("/")
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
