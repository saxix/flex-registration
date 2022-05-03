import base64
import io
import json
import logging
import tempfile
import urllib.parse
from functools import update_wrapper
from pathlib import Path

import sentry_sdk
from concurrency.api import disable_concurrency
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.db import connections, DEFAULT_DB_ALIAS
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path, reverse, reverse_lazy
from django.utils.functional import lazy
from django_redis import get_redis_connection
from redis import ResponseError

from smart_admin.site import SmartAdminSite

from smart_register import get_full_version, VERSION
from smart_register.admin.forms import ExportForm, ConsoleForm, RedisCLIForm, SQLForm
from smart_register.admin.mixin import ImportForm
from smart_register.core.utils import is_root

logger = logging.getLogger(__name__)


class AuroraAdminSite(SmartAdminSite):
    sysinfo_url = False
    site_title = ""
    site_header = lazy(lambda x: f"{get_full_version()}")

    def each_context(self, request):
        context = super().each_context(request)
        context["extra_pages"] = self.extra_pages
        return context

    def loaddata(self, request):
        context = self.each_context(request)
        form = ImportForm(request.POST, request.FILES)
        if request.method == "POST":
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    f = request.FILES["file"]
                    buf = io.BytesIO()
                    for chunk in f.chunks():
                        buf.write(chunk)
                    buf.seek(0)
                    data = json.load(buf)
                    out = io.StringIO()
                    workdir = Path(".").absolute()
                    with disable_concurrency():
                        kwargs = {
                            "dir": workdir,
                            "prefix": "~IMPORT",
                            "suffix": ".json",
                            "delete": False,
                        }
                        with tempfile.NamedTemporaryFile(**kwargs) as fdst:
                            fdst.write(json.dumps(data).encode())
                        fixture = (workdir / fdst.name).absolute()
                        try:
                            call_command("loaddata", fixture, stdout=out, verbosity=3)
                            out.write("------\n")
                            out.seek(0)
                            context["out"] = out.readlines()
                        finally:
                            fixture.unlink()
                except Exception as e:
                    self.message_user(request, f"{e.__class__.__name__}: {e} {out.getvalue()}", messages.ERROR)
            else:
                context["form"] = form
        else:
            form = ImportForm()
            context["form"] = form
        return render(request, "admin/loaddata.html", context)

    def dumpdata(self, request):
        stdout = io.StringIO()
        context = self.each_context(request)
        context["title"] = "Export Configuration"
        if request.method == "POST":
            frm = ExportForm(request.POST)
            if frm.is_valid():
                apps = frm.cleaned_data["apps"]
                call_command(
                    "dumpdata",
                    *apps,
                    stdout=stdout,
                    exclude=["registration.Record"],
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True,
                )
                return JsonResponse(
                    json.loads(stdout.getvalue()),
                    safe=False,
                    headers={"Content-Disposition": f"attachment; filename=smart-{VERSION}.json"},
                )
        else:
            frm = ExportForm()
        context["form"] = frm
        return render(request, "admin/dumpdata.html", context)

    def redis_cli(self, request, extra_context=None):
        context = self.each_context(request)
        context["title"] = "Redis CLI"
        if request.method == "POST":
            form = RedisCLIForm(request.POST)
            if form.is_valid():
                try:
                    r = get_redis_connection("default")
                    stdout = r.execute_command(form.cleaned_data["command"])
                    context["stdout"] = stdout
                except ResponseError as e:
                    messages.add_message(request, messages.ERROR, str(e))
                except Exception as e:
                    logger.exception(e)
                    messages.add_message(request, messages.ERROR, f"{e.__class__.__name__}: {e}")
        else:
            form = RedisCLIForm()
        context["form"] = form
        return render(request, "admin/redis.html", context)

    def sql(self, request, extra_context=None):
        if not is_root(request):
            raise PermissionDenied
        context = self.each_context(request)
        form = SQLForm(request.POST)
        context["form"] = form
        if request.method == "POST":
            response = {"result": [], "error": None, "stm": ""}
            if form.is_valid():
                try:
                    cmd = form.cleaned_data["command"]
                    stm = urllib.parse.unquote(base64.b64decode(cmd).decode())
                    conn = connections[DEFAULT_DB_ALIAS]
                    cursor = conn.cursor()
                    cursor.execute(stm)
                    response["result"] = cursor.fetchall()
                    response["stm"] = stm
                except Exception as e:
                    raise
                    response["error"] = str(e)
            else:
                response["error"] = str(form.errors)
            return JsonResponse(response)
        return TemplateResponse(request, "admin/sql.html", context)

    def console(self, request, extra_context=None):
        context = self.each_context(request)
        form = ConsoleForm(request.POST)
        context["form"] = form

        if not is_root(request):
            raise PermissionDenied

        if request.method == "POST":
            form = ConsoleForm(request.POST)
            if form.is_valid():
                opt = form.cleaned_data["action"]
                try:
                    if opt == "sentry":
                        sentry_sdk.capture_message("Test Message")
                        sentry_sdk.flush()
                        messages.add_message(request, messages.SUCCESS, "Done")
                    elif opt == "redis":
                        for alias, conn in settings.CACHES.items():
                            try:
                                r = get_redis_connection(alias)
                                r.execute_command("FLUSHALL ASYNC")
                                messages.add_message(request, messages.SUCCESS, f"{alias}: flushed")
                            except NotImplementedError:
                                messages.add_message(request, messages.WARNING, f"{alias}: {messages}")

                    if opt in ["400", "401", "403", "404", "500"]:
                        return HttpResponseRedirect(reverse("admin:error", args=[opt]))
                except Exception as e:
                    messages.add_message(request, messages.ERROR, f"{e.__class__.__name__}: {e}")

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
            path("loaddata/", wrap(self.loaddata), name="loaddata"),
            path("dumpdata/", wrap(self.dumpdata), name="dumpdata"),
            path("console/", wrap(self.console), name="console"),
            path("redis_cli/", wrap(self.redis_cli), name="redis_cli"),
            path("sql/", wrap(self.sql), name="sql"),
            path("error/<int:code>/", wrap(self.error), name="error"),
        ]
        self.extra_pages = [("Console", reverse_lazy("admin:console"))]
        return extra + original
