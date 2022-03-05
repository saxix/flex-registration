import json
import logging
from datetime import datetime, date, time

import jsonpickle
from django import forms
from django.contrib.admin import widgets
from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import pluralize
from django.utils.text import slugify
from strategy_field.fields import StrategyClassField

from .registry import registry, WIDGET_FOR_FORMFIELD_DEFAULTS
from .utils import jsonfy, JSONEncoder, namify

logger = logging.getLogger(__name__)


class Validator(models.Model):
    FORM = 'form'
    FIELD = 'field'
    name = CICharField(max_length=255, unique=True)
    message = models.CharField(max_length=255)
    code = models.TextField(blank=True, null=True)
    target = models.CharField(max_length=5, choices=((FORM, 'Form'), (FIELD, 'Field')))

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
        except TypeError as e:
            pass
        if not ret:
            raise ValidationError(self.message)

    # def validate_(self, value):
    #     try:
    #         import pyduktape
    #         context = pyduktape.DuktapeContext()
    #         context.set_globals(value=self.js_type(value))
    #         res = context.eval_js(self.code)
    #         if not res:
    #             raise ValidationError(self.message)
    #     except ValidationError:
    #         raise
    #     except Exception as e:
    #         logger.exception(e)
    #         raise Exception(e)


def get_validators(field):
    if field.validator:
        def inner(value):
            field.validator.validate(value)

        return [inner]
    return []


class FlexFormBaseForm(forms.Form):
    flex_form = None

    def is_valid(self):
        return super().is_valid()

    def clean(self):
        cleaned_data = self.cleaned_data
        if self.is_valid() and self.flex_form and self.flex_form.validator:
            try:
                self.flex_form.validator.validate(cleaned_data)
            except Exception as e:
                raise ValidationError(e)
        return cleaned_data


class FlexForm(models.Model):
    name = CICharField(max_length=255, unique=True)
    validator = models.ForeignKey(Validator,
                                  limit_choices_to={'target': Validator.FORM},
                                  blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):

        return self.name

    def add_formset(self, form, **extra):
        defaults = {
            'extra': 0,
            'name': form.name.lower() + pluralize(0)
        }
        defaults.update(extra)
        return FormSet.objects.create(parent=self, flex_form=form, **defaults)

    def get_form(self):
        fields = {}
        for field in self.fields.all():
            kwargs = dict(label=field.label,
                          required=field.required,
                          validators=get_validators(field),
                          )
            if field.field in WIDGET_FOR_FORMFIELD_DEFAULTS:
                kwargs = {**WIDGET_FOR_FORMFIELD_DEFAULTS[field.field], **kwargs}
            if field.choices and hasattr(field.field, 'choices'):
                kwargs['choices'] = [(k.strip(), k.strip()) for k in field.choices.split(',')]
            fields[field.name] = field.field(**kwargs)
        form_class_attrs = {
            'flex_form': self,
            **fields,

        }
        flexForm = type(FlexFormBaseForm)(f'{self.name}FlexForm', (FlexFormBaseForm,), form_class_attrs)
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
    flex_form = models.ForeignKey(FlexForm, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=30)
    name = models.CharField(max_length=30, blank=True)
    field = StrategyClassField(registry=registry)
    choices = models.CharField(max_length=2000, blank=True, null=True)
    required = models.BooleanField(default=False)
    validator = models.ForeignKey(Validator, blank=True, null=True,
                                  limit_choices_to={'target': Validator.FIELD},
                                  on_delete=models.PROTECT)

    class Meta:
        unique_together = ('name', 'flex_form'),

    def __str__(self):
        return f"{self.name} {self.field}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = namify(self.label)
        else:
            self.name = namify(self.name)

        super().save(force_insert, force_update, using, update_fields)
