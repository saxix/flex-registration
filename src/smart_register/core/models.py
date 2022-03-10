import logging
from datetime import date, datetime, time

import jsonpickle
from admin_ordering.models import OrderableModel
from django import forms
from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.template.defaultfilters import pluralize
from django_regex.fields import RegexField
from strategy_field.fields import StrategyClassField
from strategy_field.utils import fqn

from .fields import WIDGET_FOR_FORMFIELD_DEFAULTS
from .forms import FlexFormBaseForm, CustomFieldMixin
from .registry import field_registry, form_registry, import_custom_field
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
    base_type = StrategyClassField(registry=form_registry, default=FlexFormBaseForm)
    validator = models.ForeignKey(
        Validator, limit_choices_to={"target": Validator.FORM}, blank=True, null=True, on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "FlexForm"
        verbose_name_plural = "FlexForms"

    def __str__(self):
        return self.name

    def add_field(
        self,
        label,
        field_type=forms.CharField,
        required=False,
        choices=None,
        regex=None,
        validator=None,
        name=None,
        **kwargs,
    ):
        if isinstance(choices, (list, tuple)):
            kwargs["choices"] = choices
            choices = None
        return self.fields.update_or_create(
            label=label,
            defaults={
                "name": name,
                "field_type": field_type,
                "choices": choices,
                "regex": regex,
                "validator": validator,
                "advanced": kwargs,
                "required": required,
            },
        )[0]

    def add_formset(self, form, **extra):
        defaults = {"extra": 0, "name": form.name.lower() + pluralize(0)}
        defaults.update(extra)
        return FormSet.objects.update_or_create(parent=self, flex_form=form, **defaults)

    def get_form(self):
        fields = {}
        for field in self.fields.order_by("ordering"):
            try:
                fields[field.name] = field.get_instance()
            except TypeError:
                pass
        form_class_attrs = {
            "flex_form": self,
            **fields,
        }
        flexForm = type(FlexFormBaseForm)(f"{self.name}FlexForm", (self.base_type,), form_class_attrs)
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


class FlexFormField(OrderableModel):
    flex_form = models.ForeignKey(FlexForm, on_delete=models.CASCADE, related_name="fields")
    label = models.CharField(max_length=2000)
    name = CICharField(max_length=30, blank=True)
    field_type = StrategyClassField(registry=field_registry, import_error=import_custom_field)
    choices = models.CharField(max_length=2000, blank=True, null=True)
    required = models.BooleanField(default=False)
    validator = models.ForeignKey(
        Validator, blank=True, null=True, limit_choices_to={"target": Validator.FIELD}, on_delete=models.PROTECT
    )
    regex = RegexField(blank=True, null=True)
    advanced = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        unique_together = (("flex_form", "name"),)
        verbose_name = "FlexForm Field"
        verbose_name_plural = "FlexForm Fields"
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.name} {self.field_type}"

    def get_instance(self):
        # if hasattr(self.field_type, "custom") and isinstance(self.field_type.custom, CustomFieldType):
        if issubclass(self.field_type, CustomFieldMixin):
            field_type = self.field_type.custom.base_type
            kwargs = self.field_type.custom.attrs.copy()
            if self.validator:
                kwargs.setdefault("validators", get_validators(self))
            elif self.field_type.custom.validator:
                kwargs["validators"] = get_validators(self.field_type.custom)
            else:
                kwargs["validators"] = []
            kwargs.setdefault("label", self.label)
            kwargs.setdefault("required", self.required)
            regex = self.regex or self.field_type.custom.regex
        else:
            field_type = self.field_type
            kwargs = self.advanced.copy()
            regex = self.regex
            kwargs.setdefault("label", self.label)
            kwargs.setdefault("required", self.required)
            kwargs.setdefault("validators", get_validators(self))
        if field_type in WIDGET_FOR_FORMFIELD_DEFAULTS:
            kwargs = {**WIDGET_FOR_FORMFIELD_DEFAULTS[field_type], **kwargs}
        if "choices" not in kwargs and self.choices and hasattr(field_type, "choices"):
            # kwargs["choices"] = [(k.strip(), k.strip()) for k in self.choices.split(",")]
            kwargs["choices"] = clean_choices(self.choices.split(","))
        if regex:
            kwargs["validators"].append(RegexValidator(regex))
        return field_type(**kwargs)

    def clean(self):
        try:
            self.get_instance()
        except Exception as e:
            raise ValidationError(e)

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


def clean_choices(value):
    if not isinstance(value, (list, tuple)):
        raise ValueError("choices must be list or tuple")
    try:
        return list(dict(value).items())
    except ValueError:
        return list(zip(map(str.lower, value), value))


class CustomFieldType(models.Model):
    name = CICharField(max_length=100, unique=True, validators=[RegexValidator("[A-Z][a-zA-Z0-9_]*")])
    base_type = StrategyClassField(registry=field_registry, default=forms.CharField)
    attrs = models.JSONField(default=dict)
    regex = RegexField(blank=True, null=True)
    # choices = models.CharField(max_length=2000, blank=True, null=True)
    # required = models.BooleanField(default=False)
    validator = models.ForeignKey(
        Validator, blank=True, null=True, limit_choices_to={"target": Validator.FIELD}, on_delete=models.PROTECT
    )

    @staticmethod
    def build(name, defaults):
        choices = defaults.get("attrs", {}).get("choices", {})
        if choices:
            defaults["attrs"]["choices"] = clean_choices(choices)
        return CustomFieldType.objects.update_or_create(name=name, defaults=defaults)[0]

    def __str__(self):
        return self.name

    def clean(self):
        try:
            kwargs = self.attrs.copy()
            class_ = self.get_class()
            class_(**kwargs)
        except Exception as e:
            raise ValidationError(f"Error instantiating {fqn(class_)}: {e}")

    def get_class(self):
        attrs = self.attrs.copy()
        attrs["custom"] = self
        return type(self.base_type)(self.name, (CustomFieldMixin, self.base_type), attrs)
