import base64

import requests
from django import forms
from django.template.response import TemplateResponse
from requests.auth import HTTPBasicAuth

from admin_extra_buttons.decorators import button
from smart_register.core.utils import is_root
from smart_register.registration.models import Record


class DebugMixin:
    @button(permission=is_root)
    def fetch(self, request):
        class FetchForm(forms.Form):
            host = forms.URLField()
            username = forms.CharField()
            password = forms.CharField(widget=forms.PasswordInput)
            registration = forms.IntegerField()
            start = forms.IntegerField()
            end = forms.IntegerField()

            def clean(self):
                return super().clean()

        ctx = self.get_common_context(request)
        if request.method == "POST":
            form = FetchForm(request.POST)
            if form.is_valid():
                auth = HTTPBasicAuth(form.cleaned_data["username"], form.cleaned_data["password"])
                url = "{host}api/data/{registration}/{start}/{end}/".format(**form.cleaned_data)
                with requests.get(url, stream=True, auth=auth) as res:
                    if res.status_code != 200:
                        raise Exception(str(res))
                    payload = res.json()
                    for record in payload["data"]:
                        Record.objects.update_or_create(
                            registration_id=form.cleaned_data["registration"],
                            defaults={"timestamp": record["timestamp"], "storage": base64.b64decode(record["storage"])},
                        )
        else:
            form = FetchForm()

        ctx["form"] = form
        response = TemplateResponse(request, "admin/registration/record/fetch.html", ctx)
        return response
