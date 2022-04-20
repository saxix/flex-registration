import base64
import logging
import time
from hashlib import md5

import sentry_sdk
from constance import config
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile,
    UploadedFile,
)
from django.forms import forms
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.cache import get_conditional_response
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import get_language
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from smart_register.core.cache import cache_formset
from smart_register.core.utils import get_qrcode
from smart_register.registration.models import Record, Registration
from smart_register.state import state

logger = logging.getLogger(__name__)


class QRVerify(TemplateView):
    template_name = "registration/register_verify.html"

    def get_context_data(self, **kwargs):
        record = Record.objects.get(id=self.kwargs["pk"])
        valid = md5(record.storage).hexdigest() == self.kwargs["hash"]
        return super().get_context_data(valid=valid, record=record, **kwargs)


class FixedLocaleView:
    @cached_property
    def registration(self):
        raise NotImplementedError

    def dispatch(self, request, *args, **kwargs):
        # translation.activate(self.registration.locale)
        return super().dispatch(request, *args, **kwargs)


class RegisterCompleteView(FixedLocaleView, TemplateView):
    template_name = "registration/register_done.html"

    @cached_property
    def registration(self):
        return self.record.registration

    @cached_property
    def record(self):
        return Record.objects.select_related("registration").get(
            registration__id=self.kwargs["reg"], id=self.kwargs["rec"]
        )

    def get_qrcode(self, record):
        h = md5(record.storage).hexdigest()
        url = self.request.build_absolute_uri(reverse("register-done", args=[record.registration.pk, record.pk]))
        hashed_url = f"{url}/{h}"
        return get_qrcode(hashed_url), url

    def get_context_data(self, **kwargs):
        if config.QRCODE:
            qrcode, url = self.get_qrcode(self.record)
        else:
            qrcode, url = None, None
        return super().get_context_data(qrcode=qrcode, url=url, record=self.record, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(FixedLocaleView, FormView):
    template_name = "registration/register.html"

    def get(self, request, *args, **kwargs):
        if state.collect_messages:
            res_etag = str(time.time())
        else:
            res_etag = "/".join(
                [
                    str(self.registration.version),
                    get_language(),
                    {True: "staff", False: ""}[request.user.is_staff],
                ]
            )
        response = get_conditional_response(request, str(res_etag))
        if response is None:
            response = super().get(request, *args, **kwargs)
        response.headers.setdefault("ETag", res_etag)
        return response

    @cached_property
    def registration(self):
        filters = {}
        if not self.request.user.is_staff and not state.collect_messages:
            filters["active"] = True

        base = Registration.objects.select_related("flex_form", "validator")
        try:
            return base.get(slug=self.kwargs["slug"], **filters)
        except Registration.DoesNotExist:  # pragma: no cover
            raise Http404

    def get_form_class(self):
        return self.registration.flex_form.get_form()

    # def get_form(self, form_class=None):
    #     return super().get_form(form_class)
    #
    @cache_formset
    def get_formsets_classes(self):
        formsets = {}
        attrs = self.get_form_kwargs().copy()
        attrs.pop("prefix")
        for fs in self.registration.flex_form.formsets.select_related("flex_form", "parent").filter(enabled=True):
            formsets[fs.name] = fs.get_formset()
        return formsets

    def get_formsets(self):
        formsets = {}
        attrs = self.get_form_kwargs().copy()
        attrs.pop("prefix")
        for name, fs in self.get_formsets_classes().items():
            formsets[name] = fs(prefix=f"{name}", **attrs)
        return formsets

    def get_context_data(self, **kwargs):
        if "formsets" not in kwargs:
            kwargs["formsets"] = self.get_formsets()
        # kwargs["language"] = get_language_info(self.registration.locale)
        # kwargs["locale"] = self.registration.locale
        kwargs["dataset"] = self.registration

        ctx = super().get_context_data(**kwargs)
        m = forms.Media()
        m += ctx["form"].media
        for __, f in ctx["formsets"].items():
            m += f.media
        ctx["media"] = m
        return ctx

    def validate(self, cleaned_data):
        if self.registration.validator:
            try:
                self.registration.validator.validate(cleaned_data)
            except ValidationError as e:
                self.errors.append(e)
                return False
        return True

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formsets = self.get_formsets()
        self.errors = []
        is_valid = True
        all_cleaned_data = {}

        for fs in formsets.values():
            if fs.is_valid():
                all_cleaned_data[fs.fs.name] = fs.cleaned_data
            else:
                is_valid = False

        if is_valid:
            is_valid = self.validate(all_cleaned_data)

        if form.is_valid() and is_valid:
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

    def form_valid(self, form, formsets):
        data = form.cleaned_data
        for name, fs in formsets.items():
            data[name] = []
            for f in fs:
                data[name].append(f.cleaned_data)

        def parse_field(field):
            if isinstance(field, (UploadedFile, InMemoryUploadedFile, TemporaryUploadedFile)):
                content = field.read()
                if not content:
                    return ""
                return base64.b64encode(content)
            elif isinstance(field, dict):
                return {item[0]: parse_field(item[1]) for item in field.items()}
            elif isinstance(field, list):
                return [parse_field(item) for item in field]
            elif field is None:
                field = ""
            return field

        data = {field_name: parse_field(field) for field_name, field in data.items()}
        record = self.registration.add_record(data)
        success_url = reverse("register-done", args=[self.registration.pk, record.pk])
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form, formsets):
        """If the form is invalid, render the invalid form."""
        if config.LOG_POST_ERRORS:
            with sentry_sdk.push_scope() as scope:
                scope.set_extra("errors", self.errors)
                scope.set_extra("form.errors", form.errors)
                for n, f in formsets.items():
                    scope.set_extra(n, f.errors)
                scope.set_extra("target", self.target)
                logger.error("Validation Error")

        return self.render_to_response(
            self.get_context_data(form=form, invalid=True, errors=self.errors, formsets=formsets)
        )
