from django.forms import formset_factory
from django.shortcuts import render
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic.edit import FormView

from smart_register.core.utils import jsonfy
from smart_register.registration.models import Registration, Record


class DataSetListView(ListView):
    model = Registration


class DataSetView(CreateView):
    model = Registration
    fields = ()


class RegisterCompleView(TemplateView):
    template_name = "registration/register_done.html"


class RegisterView(FormView):
    template_name = "registration/register.html"
    # success_url = reverse_lazy('register-done')
    success_url = "/register/1/"

    def get_success_url(self):
        return super().get_success_url()

    @property
    def dataset(self):
        if "pk" in self.kwargs:
            return Registration.objects.get(id=self.kwargs["pk"])
        else:
            return Registration.objects.first()

    def get_form_class(self):
        return self.dataset.flex_form.get_form()

    def get_form(self, form_class=None):
        return super().get_form(form_class)

    def get_formsets(self):
        formsets = {}
        attrs = self.get_form_kwargs().copy()
        attrs.pop("prefix")
        for fs in self.dataset.flex_form.formsets.all():
            formSet = formset_factory(fs.get_form(), extra=fs.extra)
            formSet.fs = fs
            formsets[fs.name] = formSet(prefix=f"{fs.name}", **attrs)
        return formsets

    def get_context_data(self, **kwargs):
        if "formsets" not in kwargs:
            kwargs["formsets"] = self.get_formsets()
        kwargs["POST"] = dict(self.request.POST)

        return super().get_context_data(dataset=self.dataset, **kwargs)

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

        record = Record.objects.create(registration=self.dataset, data=jsonfy(data))

        return render(
            self.request,
            "registration/data.html",
            {
                "data": data,
                "POST": dict(self.request.POST),
                "record": record,
            },
        )

    def form_invalid(self, form, formsets):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form, formsets=formsets))
