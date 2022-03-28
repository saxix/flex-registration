import logging

from constance import config
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView

from smart_register.core.utils import get_qrcode
from smart_register.registration.models import Registration

logger = logging.getLogger(__name__)


class PageView(TemplateView):
    template_name = "index.html"

    def get_template_names(self):
        return [f"{self.kwargs['page']}.html"]


class HomeView(TemplateView):
    template_name = "index.html"

    def get_template_names(self):
        return [config.HOME_TEMPLATE, self.template_name]

    def get_context_data(self, **kwargs):
        selection = config.HOME_PAGE_REGISTRATIONS.split(";")
        buttons = []
        for sel in selection:
            if sel.strip():
                try:
                    slug, locale = sel.strip().split(",")
                    buttons.append(Registration.objects.get(active=True, slug=slug.strip(), locale=locale.strip()))
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
