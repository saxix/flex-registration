import io
import json
import tempfile
from pathlib import Path

from concurrency.api import disable_concurrency
from django.contrib import messages
from django.core.management import call_command
from django.forms import forms
from django.http import JsonResponse

from admin_extra_buttons.decorators import button

from admin_extra_buttons.mixins import ExtraButtonsMixin
from smart_register.core.utils import render


class ImportForm(forms.Form):
    file = forms.FileField()


class LoadDumpMixin(ExtraButtonsMixin):
    @button(label="loaddata")
    def _import(self, request):
        ctx = self.get_common_context(
            request,
            media=self.media,
            title="Import",
        )
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
                        for k, v in data.items():
                            kwargs = {"dir": workdir, "prefix": f"~IMPORT-{k}", "suffix": ".json", "delete": False}

                            with tempfile.NamedTemporaryFile(**kwargs) as fdst:
                                fdst.write(json.dumps(v).encode())
                            fixture = (workdir / fdst.name).absolute()
                            call_command("loaddata", fixture, stdout=out, verbosity=3)
                            fixture.unlink()
                            out.write("------\n")
                            # ctx['out'] = out.getvalue()
                            out.seek(0)
                            ctx["out"] = out.readlines()
                except Exception as e:
                    self.message_user(request, f"{e.__class__.__name__}: {e} {out.getvalue()}", messages.ERROR)
            else:
                ctx["form"] = form
        else:
            form = ImportForm()
            ctx["form"] = form
        return render(request, "admin/registration/registration/import.html", ctx)

    @button()
    def dumpdata(self, request):
        opts = self.model._meta
        stdout = io.StringIO()
        call_command(
            "dumpdata",
            f"{opts.app_name}.{opts.model_name}",
            stdout=stdout,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
        )
        return JsonResponse(
            json.loads(stdout.getvalue()),
            safe=False,
            headers={"Content-Disposition": f"attachment; filename={opts.model_name}.json"},
        )
