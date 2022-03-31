import base64
import logging
from hashlib import md5

import sentry_sdk
from constance import config
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile, UploadedFile
from django.forms import forms
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.translation import get_language_info
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import FormView

from smart_register.core.cache import cache_formset
from smart_register.core.utils import get_qrcode
from smart_register.registration.models import Record, Registration

logger = logging.getLogger(__name__)


class DataSetView(CreateView):
    model = Registration
    fields = ()


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
        translation.activate(self.registration.locale)
        return super().dispatch(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):
    #     translation.activate(self.registration.locale)
    #     with translation.override(self.registration.locale):
    #         return self.render_to_response(self.get_context_data())


class RegisterCompleteView(FixedLocaleView, TemplateView):
    template_name = "registration/register_done.html"

    @cached_property
    def registration(self):
        return self.record.registration

    @cached_property
    def record(self):
        return Record.objects.select_related("registration").get(
            registration__id=self.kwargs["pk"], id=self.kwargs["rec"]
        )

    def get_qrcode(self, record):
        h = md5(record.storage).hexdigest()
        url = self.request.build_absolute_uri(reverse("register", args=[record.pk, h]))
        # url = self.request.build_absolute_uri(f"/register/qr/{record.pk}/{h}")
        return get_qrcode(url), url

    def get_context_data(self, **kwargs):
        if config.QRCODE:
            qrcode, url = self.get_qrcode(self.record)
        else:
            qrcode, url = None, None
        return super().get_context_data(qrcode=qrcode, url=url, record=self.record, **kwargs)


# @method_decorator(cache_page(60 * 60), name="dispatch")
class RegisterView(FixedLocaleView, FormView):
    template_name = "registration/register.html"

    @cached_property
    def registration(self):
        filters = {}
        if not self.request.user.is_staff:
            filters["active"] = True

        base = Registration.objects.select_related("flex_form", "validator")
        try:
            return base.get(slug=self.kwargs["slug"], locale=self.kwargs["locale"], **filters)
        except Registration.DoesNotExist:  # pragma: no cover
            raise Http404

    def get_form_class(self):
        return self.registration.flex_form.get_form()

    def get_form(self, form_class=None):
        return super().get_form(form_class)

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
        # for fs in self.registration.flex_form.formsets.select_related("flex_form", "parent").filter(enabled=True):
        #     formsets[fs.name] = fs.get_formset()(prefix=f"{fs.name}", **attrs)
        return formsets

    def get_context_data(self, **kwargs):
        if "formsets" not in kwargs:
            kwargs["formsets"] = self.get_formsets()
        kwargs["language"] = get_language_info(self.registration.locale)
        kwargs["locale"] = self.registration.locale
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
            self.validate(all_cleaned_data)

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
                return base64.b64encode(field.read())
            elif isinstance(field, dict):
                return {item[0]: parse_field(item[1]) for item in field.items()}
            elif isinstance(field, list):
                return [parse_field(item) for item in field]
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
