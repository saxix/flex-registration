import json
import logging
from datetime import date, datetime, time
from json import JSONDecodeError

import jsonpickle
from admin_ordering.models import OrderableModel
from concurrency.fields import AutoIncVersionField
from django import forms
from django.contrib.postgres.fields import CICharField
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.forms import formset_factory
from django.template.defaultfilters import pluralize, slugify
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from natural_keys import NaturalKeyModel, NaturalKeyModelManager
from py_mini_racer.py_mini_racer import MiniRacerBaseException
from strategy_field.utils import fqn

from ..i18n.gettext import gettext as _
from ..i18n.models import I18NModel
from ..state import state
from . import fields
from .compat import RegexField, StrategyClassField
from .fields import WIDGET_FOR_FORMFIELD_DEFAULTS, SmartFieldMixin
from .forms import CustomFieldMixin, FlexFormBaseForm, SmartBaseFormSet
from .registry import field_registry, form_registry, import_custom_field
from .utils import JSONEncoder, dict_setdefault, jsonfy, namify, underscore_to_camelcase

logger = logging.getLogger(__name__)

cache = caches["default"]


class Validator(NaturalKeyModel):
    STATUS_ERROR = "error"
    STATUS_EXCEPTION = "exc"
    STATUS_SUCCESS = "success"
    STATUS_SKIP = "skip"
    STATUS_UNKNOWN = "unknown"
    STATUS_INACTIVE = "inactive"

    FORM = "form"
    FIELD = "field"
    MODULE = "module"
    FORMSET = "formset"
    SCRIPT = "script"
    HANDLER = "handler"

    CONSOLE = mark_safe(
        """
    console = {log: function(d) {}};
    """
    )
    LIB = mark_safe(
        """
TODAY = new Date();
dateutil = {today: TODAY};

function getAge(birthDate){
    return Math.floor((new Date() - new Date(birthDate).getTime()) / 3.15576e+10);
}


_ = {is_child: function(d) { return d && getAge(d) < 18 ? true: false},
     is_baby: function(d) { return d && getAge(d) <= 2 ? true: false},
     is_future: function(d) { return d  && Date.parse(d) > dateutil.today ? true: false},
};
_.is_adult = function(d) { return !_.is_child(d)};

"""
    )

    version = AutoIncVersionField()
    last_update_date = models.DateTimeField(auto_now=True)

    label = CICharField(max_length=255)
    name = CICharField(verbose_name=_("Function Name"), max_length=255, unique=True, blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    target = models.CharField(
        max_length=10,
        choices=(
            (FORM, "Form"),
            (FIELD, "Field"),
            (FORMSET, "Formset"),
            (MODULE, "Module"),
            (HANDLER, "Handler"),
            (SCRIPT, "Script"),
        ),
    )
    trace = models.BooleanField(
        default=False,
        help_text="Debug/Testing purposes: trace validator invocation on Sentry.",
    )
    count_errors = models.BooleanField(default=False, help_text="Count failures")
    active = models.BooleanField(default=False, blank=True, help_text="Enable/Disable validator.")
    draft = models.BooleanField(
        default=False, blank=True, help_text="Testing purposes: draft validator are enabled only for staff users."
    )
    _natural_key = ["name"]

    def __str__(self):
        return f"{self.label} ({self.target})"

    @staticmethod
    def js_type(value):
        if isinstance(value, (datetime, date, time)):
            return str(value)
        if isinstance(value, (dict,)):
            return jsonfy(value)
        return value

    def jspickle(self, value):
        return json.dumps(value, cls=JSONEncoder, skip_files=True)

    def monitor(self, status, value, exc: Exception = None):
        cache.set(f"validator-{state.request.user.pk}-{self.pk}-status", status)
        error = None
        if exc:
            if hasattr(exc, "error_dict"):
                error = self.jspickle(
                    exc.error_dict,
                )
            elif isinstance(exc, ValidationError):
                error = self.jspickle({"Error": exc.messages})
            else:
                error = self.jspickle({"Error": str(exc)})
        cache.set(f"validator-{state.request.user.pk}-{self.pk}-error", error)
        cache.set(f"validator-{state.request.user.pk}-{self.pk}-payload", self.jspickle(value))

    def validate(self, value, registration=None):
        from py_mini_racer import MiniRacer

        if self.active:
            self.monitor(self.STATUS_UNKNOWN, value)
        else:
            self.monitor(self.STATUS_INACTIVE, value)

        if self.active or (self.draft and state.request.user.is_staff):
            ctx = MiniRacer()
            try:
                pickled = self.jspickle(value or "")
                ctx.eval(f"{self.CONSOLE};{self.LIB}; var value = {pickled};")
                result = ctx.eval(self.code)
                if result is None:
                    ret = False
                else:
                    try:
                        ret = jsonpickle.decode(result)
                    except (JSONDecodeError, TypeError):
                        ret = result
                if isinstance(ret, str):
                    raise ValidationError(_(ret))
                elif isinstance(ret, (list, tuple)):
                    errors = [_(v) for v in ret]
                    raise ValidationError(errors)
                elif isinstance(ret, dict):
                    errors = {k: _(v) for (k, v) in ret.items()}
                    raise ValidationError(errors)
                elif isinstance(ret, bool) and not ret:
                    raise ValidationError(_("Please insert a valid value"))
            except ValidationError as e:
                import sentry_sdk

                if self.trace:
                    with sentry_sdk.push_scope() as scope:
                        scope.set_tag("validator", self.name)
                        scope.set_extra("registration", registration)
                        logger.exception(e)
                    self.monitor(self.STATUS_ERROR, value, e)
                elif self.count_errors:
                    with sentry_sdk.push_scope() as scope:
                        scope.set_tag("validator", self.name)
                        scope.set_extra("registration", registration)
                        sentry_sdk.capture_message(f"{self.name}", level="info")
                raise
            except MiniRacerBaseException as e:
                logger.exception(e)
                self.monitor(self.STATUS_EXCEPTION, value, e)
                return True
            except Exception as e:
                logger.exception(e)
                self.monitor(self.STATUS_EXCEPTION, value, e)
                raise
            self.monitor(self.STATUS_SUCCESS, value)

        elif self.trace:
            self.monitor(self.STATUS_SKIP, value)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = namify(self.label)
        super().save(force_insert, force_update, using, update_fields)

    def get_script_url(self):
        return reverse("api:validator-script", args=[self.name])


def get_validators(field):
    if field.validator:

        def inner(value):
            field.validator.validate(value)

        return [inner]
    return []


class FlexForm(I18NModel, NaturalKeyModel):
    version = AutoIncVersionField()
    last_update_date = models.DateTimeField(auto_now=True)
    name = CICharField(max_length=255, unique=True)
    base_type = StrategyClassField(registry=form_registry, default=FlexFormBaseForm)
    validator = models.ForeignKey(
        Validator, limit_choices_to={"target": Validator.FORM}, blank=True, null=True, on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "Flex Form"
        verbose_name_plural = "Flex Forms"

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
        return FormSet.objects.update_or_create(parent=self, flex_form=form, defaults=defaults)[0]

    # @cache_form
    def get_form_class(self):
        from aurora.core.fields import CompilationTimeField

        fields = {}
        compilation_time_field = None
        indexes = FlexFormBaseForm.indexes.copy()
        for field in self.fields.filter(enabled=True).select_related("validator").order_by("ordering"):
            try:
                fld = field.get_instance()
                fields[field.name] = fld
                if isinstance(fld, CompilationTimeField):
                    compilation_time_field = field.name
                if index := field.advanced.get("smart", {}).get("index"):
                    indexes[str(index)] = field.name
            except TypeError:
                pass
        form_class_attrs = {
            "flex_form": self,
            "compilation_time_field": compilation_time_field,
            "indexes": indexes,
            **fields,
        }
        flexForm = type(f"{self.name}FlexForm", (self.base_type,), form_class_attrs)
        return flexForm

    def get_formsets_classes(self):
        formsets = {}
        for fs in self.formsets.select_related("flex_form", "parent").filter(enabled=True):
            formsets[fs.name] = fs.get_formset()
        return formsets

    def get_formsets(self, attrs):
        formsets = {}
        for name, fs in self.get_formsets_classes().items():
            formsets[name] = fs(prefix=f"{name}", **attrs)
        return formsets

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)


class FormSet(NaturalKeyModel, OrderableModel):
    FORMSET_DEFAULT_ATTRS = {
        "smart": {
            "title": {
                "class": "",
                "html_attrs": {},
            },
            "container": {
                "class": "",
                "html_attrs": {},
            },
            "widget": {
                "showCounter": False,
                "counterPrefix": "",
                "addText": "Add Another",
                "addCssClass": None,
                "deleteText": "Remove",
                "deleteCssClass": None,
                "keepFieldValues": False,
                "onAdd": None,
                "onRemove": None,
            },
        }
    }
    version = AutoIncVersionField()
    last_update_date = models.DateTimeField(auto_now=True)

    name = CICharField(max_length=255)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    enabled = models.BooleanField(default=True)

    parent = models.ForeignKey(FlexForm, on_delete=models.CASCADE, related_name="formsets")
    flex_form = models.ForeignKey(FlexForm, on_delete=models.CASCADE)
    extra = models.IntegerField(default=0, blank=False, null=False)
    max_num = models.IntegerField(default=None, blank=True, null=True)
    min_num = models.IntegerField(default=0, blank=False, null=False)

    dynamic = models.BooleanField(default=True)
    validator = models.ForeignKey(
        Validator, blank=True, null=True, limit_choices_to={"target": Validator.FORMSET}, on_delete=models.SET_NULL
    )

    advanced = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "FormSet"
        verbose_name_plural = "FormSets"
        ordering = ["ordering"]
        unique_together = (("parent", "flex_form", "name"),)

    def __str__(self):
        return self.name

    def get_form(self):
        return self.flex_form.get_form_class()

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        dict_setdefault(self.advanced, self.FORMSET_DEFAULT_ATTRS)
        super().save(*args, **kwargs)

    @cached_property
    def widget_attrs(self):
        dict_setdefault(self.advanced, self.FORMSET_DEFAULT_ATTRS)
        return self.advanced["smart"]["widget"]

    def get_formset(self):
        formSet = formset_factory(
            self.get_form(),
            formset=SmartBaseFormSet,
            extra=self.extra,
            min_num=self.min_num,
            absolute_max=self.max_num,
            max_num=self.max_num,
        )
        formSet.fs = self
        formSet.required = self.min_num > 0
        return formSet


FIELD_KWARGS = {
    forms.CharField: {"min_length": None, "max_length": None, "empty_value": "", "initial": None},
    forms.IntegerField: {"min_value": None, "max_value": None, "initial": None},
    forms.DateField: {"initial": None},
    fields.LocationField: {},
    fields.RemoteIpField: {},
    fields.AjaxSelectField: {},
    fields.SmartFileField: {},
    fields.SelectField: {},
    fields.WebcamField: {},
}


class FlexFormField(NaturalKeyModel, I18NModel, OrderableModel):
    I18N_FIELDS = [
        "label",
    ]
    I18N_ADVANCED = ["smart.hint", "smart.question", "smart.description"]
    FLEX_FIELD_DEFAULT_ATTRS = {
        "widget_kwargs": {
            "pattern": None,
            "title": None,
            "placeholder": None,
        },
        "kwargs": {},
        "smart": {
            "hint": "",
            "visible": True,
            "onchange": "",
            "question": "",
            "description": "",
            "index": None,
            "fieldset": "",
        },
    }

    version = AutoIncVersionField()
    last_update_date = models.DateTimeField(auto_now=True)

    flex_form = models.ForeignKey(FlexForm, on_delete=models.CASCADE, related_name="fields")
    label = models.CharField(max_length=2000)
    name = CICharField(max_length=100, blank=True)
    field_type = StrategyClassField(registry=field_registry, import_error=import_custom_field)
    choices = models.CharField(max_length=2000, blank=True, null=True)
    required = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    validator = models.ForeignKey(
        Validator, blank=True, null=True, limit_choices_to={"target": Validator.FIELD}, on_delete=models.PROTECT
    )
    regex = RegexField(blank=True, null=True)
    advanced = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        unique_together = (("flex_form", "name"),)
        verbose_name = "Flex Field"
        verbose_name_plural = "Flex Fields"
        ordering = ["ordering"]

    def __str__(self):
        if self.field_type:
            return f"{self.name} {self.field_type.__name__}"
        return f"{self.name} <no type>"

    def type_name(self):
        return str(self.field_type.__name__)

    def fqn(self):
        return fqn(self.field_type)

    def get_field_kwargs(self):
        if issubclass(self.field_type, CustomFieldMixin):
            widget_kwargs = {}
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
            advanced = self.advanced.copy()
            kwargs = self.advanced.get("kwargs", {}).copy()
            widget_kwargs = self.advanced.get("widget_kwargs", {}).copy()
            regex = self.regex

            smart_attrs = advanced.pop("smart", {}).copy()
            # data = kwargs.pop("data", {}).copy()
            smart_attrs["data-flex"] = self.name
            if not smart_attrs.get("visible", True):
                smart_attrs["data-visibility"] = "hidden"
            elif smart_attrs.get("question", ""):
                smart_attrs["data-visibility"] = "hidden"

            kwargs.setdefault("smart_attrs", smart_attrs.copy())
            kwargs.setdefault("label", self.label)
            kwargs.setdefault("required", self.required)
            kwargs.setdefault("validators", get_validators(self))
        if field_type in WIDGET_FOR_FORMFIELD_DEFAULTS:
            kwargs = {**WIDGET_FOR_FORMFIELD_DEFAULTS[field_type], **kwargs}
        if "datasource" in self.advanced:
            kwargs["datasource"] = self.advanced["datasource"]
        if hasattr(field_type, "choices"):
            if "choices" in self.advanced:
                kwargs["choices"] = self.advanced["choices"]
            elif self.choices:
                kwargs["choices"] = clean_choices(self.choices.split(","))
        if regex:
            kwargs["validators"].append(RegexValidator(regex))
        kwargs["widget_kwargs"] = widget_kwargs
        return kwargs

    def get_instance(self):
        try:
            if issubclass(self.field_type, CustomFieldMixin):
                field_type = self.field_type.custom.base_type
            else:
                field_type = self.field_type
            kwargs = self.get_field_kwargs()
            kwargs.setdefault("flex_field", self)
            tt = type(field_type.__name__, (SmartFieldMixin, field_type), dict())
            fld = tt(**kwargs)
        except Exception as e:
            logger.exception(e)
            raise
        return fld

    def clean(self):
        if self.field_type:
            try:
                # dict_setdefault(self.advanced, self.FLEX_FIELD_DEFAULT_ATTRS)
                # dict_setdefault(self.advanced, {"kwargs": FIELD_KWARGS.get(self.field_type, {})})
                self.get_instance()
            except Exception as e:
                logger.exception(e)
                raise ValidationError(e)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = namify(self.label)[:100]
        else:
            self.name = namify(self.name)[:100]

        super().save(force_insert, force_update, using, update_fields)


class OptionSetManager(NaturalKeyModelManager):
    def get_from_cache(self, name):
        key = f"option-set-{name}"
        value = cache.get(key)
        if value is None:
            value = self.get(name=name)
            cache.set(key, value)
        return value


class OptionSet(NaturalKeyModel, models.Model):
    version = AutoIncVersionField()
    last_update_date = models.DateTimeField(auto_now=True)
    name = CICharField(max_length=100, unique=True, validators=[RegexValidator("[a-z0-9-_]")])
    description = models.CharField(max_length=1000, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    separator = models.CharField(max_length=1, default="", blank=True)
    comment = models.CharField(max_length=1, default="#", blank=True)
    columns = models.CharField(
        max_length=20, default="0,0,-1", blank=True, help_text="column order. Es: 'pk,parent,label' or 'pk,label'"
    )

    pk_col = models.IntegerField(default=0, help_text="ID column number")
    parent_col = models.IntegerField(default=-1, help_text="Column number of the indicating parent element")
    locale = models.CharField(max_length=5, default="en-us", help_text="default language code")
    languages = models.CharField(
        max_length=255, default="-;-;", blank=True, null=True, help_text="language code of each column."
    )
    _natural_key = ["name"]

    objects = OptionSetManager()

    def __str__(self):
        return self.name

    def clean(self):
        if self.locale not in self.languages:
            raise ValidationError("Default locale must be in the languages list")
        try:
            self.languages.split(",")
        except ValueError:
            raise ValidationError("Languages must be a comma separated list of locales")

    def get_cache_key(self, requested_language):
        return f"options-{self.pk}-{requested_language}-{self.version}"

    def get_api_url(self):
        return reverse("optionset", args=[self.name])

    def get_data(self, requested_language=None):
        if self.separator and requested_language:
            try:
                label_col = self.languages.split(",").index(requested_language)
            except ValueError:
                logger.error(f"Language {requested_language} not available for OptionSet {self.name}")
                label_col = self.languages.split(",").index(self.locale)
        else:
            label_col = 0

        key = self.get_cache_key(requested_language)
        value = cache.get(key, version=self.version)
        if not value:
            value = []
            for line in self.data.split("\r\n"):
                if not line.strip():
                    continue
                if line.startswith(self.comment):
                    continue
                parent = None
                if self.separator:
                    cols = line.split(self.separator)
                    pk = cols[self.pk_col]
                    label = cols[label_col]
                    if self.parent_col > 0:
                        parent = cols[self.parent_col]
                else:
                    label = line
                    pk = str(line).lower()

                values = {
                    "pk": pk,
                    "parent": parent,
                    "label": label,
                }
                value.append(values)
            cache.set(key, value)
        return value

    def as_choices(self, language=None):
        data = self.get_data(language or get_language())
        for entry in data:
            yield entry["pk"], entry["label"]

    def as_json(self, language=None):
        return self.get_data(language or get_language())


def clean_choices(value):
    if not isinstance(value, (list, tuple)):
        raise ValueError("choices must be list or tuple")
    try:
        return list(dict(value).items())
    except ValueError:
        return list(zip(map(str.lower, value), value))


class CustomFieldType(NaturalKeyModel, models.Model):
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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        cls = self.get_class()
        if fqn(cls) not in field_registry:
            field_registry.register(cls)

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
        return type(self.base_type)(underscore_to_camelcase(self.name), (CustomFieldMixin, self.base_type), attrs)
