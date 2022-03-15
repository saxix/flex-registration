from constance import config
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "index.html"


class MaintenanceView(TemplateView):
    template_name = "maintenance.html"

    def get(self, request, *args, **kwargs):
        if not config.MAINTENANCE_MODE:
            return HttpResponseRedirect("/")
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
