from django.forms import formset_factory
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import get_language_info
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import FormView

from smart_register.registration.models import Registration, Record


class DataSetView(CreateView):
    model = Registration
    fields = ()


class RegisterCompleView(TemplateView):
    template_name = "registration/register_done.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            record=Record.objects.get(registration__id=self.kwargs["pk"], id=self.kwargs["rec"]), **kwargs
        )


class RegisterView(FormView):
    template_name = "registration/register.html"

    @property
    def registration(self):
        try:
            if "pk" in self.kwargs:
                return Registration.objects.get(active=True, id=self.kwargs["pk"])
            else:
                return Registration.objects.filter(active=True).latest()
        except Exception:  # pragma: no cover
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
            formSet = formset_factory(fs.get_form(), extra=fs.extra)
            formSet.fs = fs
            formSet.required = fs.required
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
