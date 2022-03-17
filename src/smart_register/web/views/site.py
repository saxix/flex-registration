from constance import config
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "index.html"

    def get_template_names(self):
        return [config.HOME_TEMPLATE, self.template_name]


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
