import base64
import io
from hashlib import md5
from pathlib import Path

import qrcode
from constance import config
from django.conf import settings
from django.forms import formset_factory
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import get_language_info
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import FormView
from PIL import Image

from smart_register.registration.models import Record, Registration


class DataSetView(CreateView):
    model = Registration
    fields = ()


class QRVerify(TemplateView):
    template_name = "registration/register_verify.html"

    def get_context_data(self, **kwargs):
        record = Record.objects.get(id=self.kwargs["pk"])
        valid = md5(record.storage).hexdigest() == self.kwargs["hash"]
        return super().get_context_data(valid=valid, record=record, **kwargs)


class RegisterCompleteView(TemplateView):
    template_name = "registration/register_done.html"

    def get_qrcode(self, record):
        logo_link = Path(settings.BASE_DIR) / "web/static/unicef_logo.jpeg"
        logo = Image.open(logo_link)
        basewidth = 100
        wpercent = basewidth / float(logo.size[0])
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
        QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        h = md5(record.storage).hexdigest()
        url = self.request.build_absolute_uri(f"/register/qr/{record.pk}/{h}")
        QRcode.add_data(url)
        QRcode.make()
        QRimg = QRcode.make_image(fill_color="black", back_color="white").convert("RGB")

        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)
        buff = io.BytesIO()
        # save the QR code generated
        QRimg.save(buff, format="PNG")
        return base64.b64encode(buff.getvalue()).decode(), url

    def get_context_data(self, **kwargs):
        record = Record.objects.get(registration__id=self.kwargs["pk"], id=self.kwargs["rec"])
        if config.QRCODE:
            qrcode, url = self.get_qrcode(record)
        else:
            qrcode, url = None, None
        return super().get_context_data(qrcode=qrcode, url=url, record=record, **kwargs)


class RegisterView(FormView):
    template_name = "registration/register.html"

    @property
    def registration(self):
        filters = {}
        if not self.request.user.is_staff:
            filters["active"] = True
        base = Registration.objects.select_related("flex_form")
        try:
            if "pk" in self.kwargs:
                return base.get(id=self.kwargs["pk"], **filters)
            else:
                return base.filter(**filters).latest()
        except Registration.DoesNotExist:  # pragma: no cover
            raise Http404

    def get_form_class(self):
        return self.registration.flex_form.get_form()

    def get_form(self, form_class=None):
        return super().get_form(form_class)

    def get_formsets(self):
        formsets = {}
        attrs = self.get_form_kwargs().copy()
        attrs.pop("prefix")
        for fs in self.registration.flex_form.formsets.all():
            formSet = formset_factory(
                fs.get_form(), extra=fs.extra, min_num=fs.min_num, absolute_max=fs.max_num, max_num=fs.max_num
            )
            formSet.fs = fs
            formSet.required = fs.min_num > 0
            formsets[fs.name] = formSet(prefix=f"{fs.name}", **attrs)
        return formsets

    def get_context_data(self, **kwargs):
        if "formsets" not in kwargs:
            kwargs["formsets"] = self.get_formsets()
        kwargs["language"] = get_language_info(self.registration.locale)
        kwargs["POST"] = dict(self.request.POST)

        return super().get_context_data(dataset=self.registration, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formsets = self.get_formsets()
        is_valid = True
        for fs in formsets.values():
            for f in fs:
                is_valid = is_valid and f.is_valid()
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

        record = self.registration.add_record(data)
        success_url = reverse("register-done", args=[self.registration.pk, record.pk])
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form, formsets):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form, formsets=formsets))
