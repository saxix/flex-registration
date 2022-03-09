import warnings

import django
from captcha.conf import settings
from captcha.fields import CaptchaField
from captcha.models import CaptchaStore
from django.core.exceptions import ImproperlyConfigured
from django.forms.widgets import HiddenInput, MultiWidget, TextInput
from django.template.loader import render_to_string
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

from smart_register.core.fields.widgets import SmartTextWidget


class CaptchaAnswerInput(SmartTextWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs=attrs)

    """Text input for captcha answer."""

    # Use *args and **kwargs because signature changed in Django 1.11
    def build_attrs(self, *args, **kwargs):
        """Disable automatic corrections and completions."""
        attrs = super(CaptchaAnswerInput, self).build_attrs(*args, **kwargs)
        attrs["autocapitalize"] = "off"
        attrs["autocomplete"] = "off"
        attrs["autocorrect"] = "off"
        attrs["spellcheck"] = "false"
        return attrs


class BaseCaptchaTextInput(MultiWidget):
    """
    Base class for Captcha widgets
    """

    def __init__(self, attrs=None):
        widgets = (HiddenInput(attrs), CaptchaAnswerInput(attrs))
        super(BaseCaptchaTextInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(",")
        return [None, None]

    def fetch_captcha_store(self, name, value, attrs=None, generator=None):
        """
        Fetches a new CaptchaStore
        This has to be called inside render
        """
        try:
            reverse("captcha-image", args=("dummy",))
        except NoReverseMatch:
            raise ImproperlyConfigured(
                "Make sure you've included captcha.urls as explained in the INSTALLATION section on http://readthedocs.org/docs/django-simple-captcha/en/latest/usage.html#installation"
            )

        if settings.CAPTCHA_GET_FROM_POOL:
            key = CaptchaStore.pick()
        else:
            key = CaptchaStore.generate_key(generator)

        # these can be used by format_output and render
        self._value = [key, ""]
        self._key = key
        self.id_ = self.build_attrs(attrs).get("id", None)

    def id_for_label(self, id_):
        if id_:
            return id_ + "_1"
        return id_

    def image_url(self):
        return reverse("captcha-image", kwargs={"key": self._key})

    def audio_url(self):
        return reverse("captcha-audio", kwargs={"key": self._key}) if settings.CAPTCHA_FLITE_PATH else None

    def refresh_url(self):
        return reverse("captcha-refresh")


class CaptchaTextInput(BaseCaptchaTextInput):

    template_name = "captcha/widgets/captcha.html"

    def __init__(
        self,
        attrs=None,
        field_template=None,
        id_prefix=None,
        generator=None,
        output_format=None,
    ):
        self.id_prefix = id_prefix
        self.generator = generator
        if field_template is not None:
            msg = "CaptchaTextInput's field_template argument is deprecated in favor of widget's template_name."
            warnings.warn(msg, DeprecationWarning)
        self.field_template = field_template or settings.CAPTCHA_FIELD_TEMPLATE
        if output_format is not None:
            msg = "CaptchaTextInput's output_format argument is deprecated in favor of widget's template_name."
            warnings.warn(msg, DeprecationWarning)
        self.output_format = output_format or settings.CAPTCHA_OUTPUT_FORMAT
        # Fallback to custom rendering in Django < 1.11
        if not hasattr(self, "_render") and self.field_template is None and self.output_format is None:
            self.field_template = "captcha/field.html"

        if self.output_format:
            for key in ("image", "hidden_field", "text_field"):
                if "%%(%s)s" % key not in self.output_format:
                    raise ImproperlyConfigured(
                        "All of %s must be present in your CAPTCHA_OUTPUT_FORMAT setting. Could not find %s"
                        % (
                            ", ".join(["%%(%s)s" % k for k in ("image", "hidden_field", "text_field")]),
                            "%%(%s)s" % key,
                        )
                    )

        super(CaptchaTextInput, self).__init__(attrs)

    def build_attrs(self, *args, **kwargs):
        ret = super(CaptchaTextInput, self).build_attrs(*args, **kwargs)
        if self.id_prefix and "id" in ret:
            ret["id"] = "%s_%s" % (self.id_prefix, ret["id"])
        return ret

    def id_for_label(self, id_):
        ret = super(CaptchaTextInput, self).id_for_label(id_)
        if self.id_prefix and "id" in ret:
            ret = "%s_%s" % (self.id_prefix, ret)
        return ret

    def get_context(self, name, value, attrs):
        """Add captcha specific variables to context."""
        context = super(CaptchaTextInput, self).get_context(name, value, attrs)
        context["image"] = self.image_url()
        context["audio"] = self.audio_url()
        return context

    def format_output(self, rendered_widgets):
        # hidden_field, text_field = rendered_widgets
        if self.output_format:
            ret = self.output_format % {
                "image": self.image_and_audio,
                "hidden_field": self.hidden_field,
                "text_field": self.text_field,
            }
            return ret

        elif self.field_template:
            context = {
                "image": mark_safe(self.image_and_audio),
                "hidden_field": mark_safe(self.hidden_field),
                "text_field": mark_safe(self.text_field),
            }
            return render_to_string(self.field_template, context)

    def _direct_render(self, name, attrs):
        """Render the widget the old way - using field_template or output_format."""
        context = {
            "image": self.image_url(),
            "name": name,
            "key": self._key,
            "id": "%s_%s" % (self.id_prefix, attrs.get("id")) if self.id_prefix else attrs.get("id"),
            "audio": self.audio_url(),
        }
        self.image_and_audio = render_to_string(settings.CAPTCHA_IMAGE_TEMPLATE, context)
        self.hidden_field = render_to_string(settings.CAPTCHA_HIDDEN_FIELD_TEMPLATE, context)
        self.text_field = render_to_string(settings.CAPTCHA_TEXT_FIELD_TEMPLATE, context)
        return self.format_output(None)

    def render(self, name, value, attrs=None, renderer=None):
        self.fetch_captcha_store(name, value, attrs, self.generator)

        if self.field_template or self.output_format:
            return self._direct_render(name, attrs)

        extra_kwargs = {}
        if django.VERSION >= (1, 11):
            # https://docs.djangoproject.com/en/1.11/ref/forms/widgets/#django.forms.Widget.render
            extra_kwargs["renderer"] = renderer

        return super(CaptchaTextInput, self).render(name, self._value, attrs=attrs, **extra_kwargs)


class SmartCaptchaField(CaptchaField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = kwargs.pop(
            "widget",
            CaptchaTextInput(
                output_format=kwargs.pop("output_format", None),
                id_prefix=kwargs.pop("id_prefix", None),
                generator=kwargs.pop("generator", None),
            ),
        )
        super(SmartCaptchaField, self).__init__(*args, **kwargs)
