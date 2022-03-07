import logging
from datetime import date, datetime, time

import jsonpickle
from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import pluralize
from django_regex.fields import RegexField
from strategy_field.fields import StrategyClassField

from .fields import WIDGET_FOR_FORMFIELD_DEFAULTS
from .forms import FlexFormBaseForm
from .registry import registry
from .utils import jsonfy, namify

logger = logging.getLogger(__name__)


class Validator(models.Model):
    FORM = "form"
    FIELD = "field"
    name = CICharField(max_length=255, unique=True)
    message = models.CharField(max_length=255)
    code = models.TextField(blank=True, null=True)
    target = models.CharField(max_length=5, choices=((FORM, "Form"), (FIELD, "Field")))

    def __str__(self):
        return self.name

    @staticmethod
    def js_type(value):
        if isinstance(value, (datetime, date, time)):
            return str(value)
        if isinstance(value, (dict,)):
            return jsonfy(value)
        return value

    def validate(self, value):
        from py_mini_racer import MiniRacer

        ctx = MiniRacer()
        ctx.eval(f"var value = {jsonpickle.encode(value)};")
        ret = ctx.eval(self.code)
        try:
            ret = jsonpickle.decode(ret)
        except TypeError:
            pass
        if not ret:
            raise ValidationError(self.message)


def get_validators(field):
    if field.validator:

        def inner(value):
            field.validator.validate(value)

        return [inner]
    return []


class FlexForm(models.Model):
    name = CICharField(max_length=255, unique=True)
    validator = models.ForeignKey(
        Validator, limit_choices_to={"target": Validator.FORM}, blank=True, null=True, on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "FlexForm"
        verbose_name_plural = "FlexForms"

    def __str__(self):

        return self.name

    def add_formset(self, form, **extra):
        defaults = {"extra": 0, "name": form.name.lower() + pluralize(0)}
        defaults.update(extra)
        return FormSet.objects.create(parent=self, flex_form=form, **defaults)

    def get_form(self):
        fields = {}
        for field in self.fields.all():
            kwargs = dict(
                label=field.label,
                required=field.required,
                validators=get_validators(field),
            )
            if field.field_type in WIDGET_FOR_FORMFIELD_DEFAULTS:
                kwargs = {**WIDGET_FOR_FORMFIELD_DEFAULTS[field.field_type], **kwargs}
            if field.choices and hasattr(field.field_type, "choices"):
                kwargs["choices"] = [(k.strip(), k.strip()) for k in field.choices.split(",")]
            fields[field.name] = field.field_type(**kwargs)
        form_class_attrs = {
            "flex_form": self,
            **fields,
        }
        flexForm = type(FlexFormBaseForm)(f"{self.name}FlexForm", (FlexFormBaseForm,), form_class_attrs)
        return flexForm


class FormSet(models.Model):
    name = CICharField(max_length=255, unique=True)
    parent = models.ForeignKey(FlexForm, on_delete=models.CASCADE, related_name="formsets")
    flex_form = models.ForeignKey(FlexForm, on_delete=models.CASCADE)
    extra = models.IntegerField(default=0, blank=False, null=False)
    dynamic = models.BooleanField(default=True)

    class Meta:
        verbose_name = "FormSet"
        verbose_name_plural = "FormSets"

    def __str__(self):
        return self.name

    def get_form(self):
        return self.flex_form.get_form()


class FlexFormField(models.Model):
    flex_form = models.ForeignKey(FlexForm, on_delete=models.CASCADE, related_name="fields")
    label = models.CharField(max_length=30)
    name = CICharField(max_length=30, blank=True)
    field_type = StrategyClassField(registry=registry)
    choices = models.CharField(max_length=2000, blank=True, null=True)
    required = models.BooleanField(default=False)
    validator = models.ForeignKey(
        Validator, blank=True, null=True, limit_choices_to={"target": Validator.FIELD}, on_delete=models.PROTECT
    )
    regex = RegexField(blank=True, null=True)
    advanced = models.JSONField(default=dict)

    class Meta:
        unique_together = (("name", "flex_form"),)
        verbose_name = "FlexForm Field"
        verbose_name_plural = "FlexForm Fields"

    def __str__(self):
        return f"{self.name} {self.field_type}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = namify(self.label)
        else:
            self.name = namify(self.name)

        super().save(force_insert, force_update, using, update_fields)


class OptionSet(models.Model):
    name = CICharField(max_length=100)
    data = models.TextField(blank=True, null=True)
    separator = models.CharField(max_length=1, default="", blank=True)


class CustomFieldType(models.Model):
    name = CICharField(max_length=100, unique=True)
    attrs = models.JSONField(default=dict)
    regex = RegexField(blank=True, null=True)
    clean = models.TextField(blank=True, null=True)
