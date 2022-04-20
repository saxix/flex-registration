from functools import update_wrapper

from cfgv import ValidationError
from django import forms
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path, reverse, reverse_lazy
from django.utils.functional import lazy
from smart_admin.site import SmartAdminSite

from smart_register import get_full_version


class ConsoleForm(forms.Form):
    ACTIONS = [
        # ("redis", "Flush all Redis cache"),
        ("400", "raise Error 400"),
        ("401", "raise Error 401"),
        ("403", "raise Error 403"),
        ("404", "raise Error 404"),
        ("500", "raise Error 500"),
    ]

    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)


class AuroraAdminSite(SmartAdminSite):
    sysinfo_url = False
    site_title = "Aurora"
    site_header = lazy(lambda x: f"Aurora {get_full_version()}")

    def each_context(self, request):
        context = super().each_context(request)
        context["extra_pages"] = self.extra_pages
        return context

    def console(self, request, extra_context=None):
        context = self.each_context(request)

        if request.method == "POST":
            form = ConsoleForm(request.POST)
            if form.is_valid():
                opt = form.cleaned_data["action"]
                # if opt == "redis":
                #     for alias, conn in settings.CACHES.items():
                #         try:
                #             r = get_redis_connection("chat")
                #             r.execute_command("FLUSHALL ASYNC")
                #             messages.add_message(request, messages.SUCCESS, f"{alias}: flushed")
                #         except NotImplementedError:
                #             messages.add_message(request, messages.WARNING, f"{alias}: {messages}")

                if opt in ["400", "401", "403", "404", "500"]:
                    return HttpResponseRedirect(reverse("admin:error", args=[opt]))
        else:
            form = ConsoleForm()
        context["form"] = form
        return TemplateResponse(request, "admin/console.html", context)

    def error(self, request, code, extra_context=None):
        if code == 400:
            raise ValidationError("")
        elif code == 403:
            raise PermissionDenied()
        elif code == 404:
            raise Http404
        else:
            raise Exception("Raw Exception")

    def admin_sysinfo(self, request):
        from django_sysinfo.api import get_sysinfo

        infos = get_sysinfo(request)
        infos.setdefault("extra", {})
        infos.setdefault("checks", {})
        context = self.each_context(request)
        context.update(
            {
                "title": "sysinfo",
                "extra_pages": self.extra_pages,
                "infos": infos,
                "enable_switch": True,
                "has_permission": True,
            }
        )
        return render(request, "admin/sysinfo/sysinfo.html", context)

    def get_urls(self):
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        original = super().get_urls()

        extra = [
            path("console/", wrap(self.console), name="console"),
            path("error/<int:code>/", wrap(self.error), name="error"),
        ]
        self.extra_pages = [("Console", reverse_lazy("admin:console"))]
        return extra + original
