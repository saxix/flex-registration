import csv

from adminactions.api import delimiters, quotes
from django import forms
from django.conf import settings
from django.utils.translation import gettext as _


class LanguageForm(forms.Form):
    locale = forms.ChoiceField(choices=settings.LANGUAGES)


class ImportForm(forms.Form):
    file = forms.FileField()


class TemplateForm(forms.Form):
    locale = forms.ChoiceField(choices=(["-", _("Any Language")],) + settings.LANGUAGES)


class ImportLanguageForm(forms.Form):
    locale = forms.ChoiceField(choices=settings.LANGUAGES)
    csv_file = forms.FileField(widget=forms.FileInput(attrs={"accept": ".csv"}))


class CSVOptionsForm(forms.Form):
    defaults = {
        "date_format": "d/m/Y",
        "datetime_format": "N j, Y, P",
        "time_format": "P",
        "header": False,
        "quotechar": '"',
        "quoting": csv.QUOTE_ALL,
        "delimiter": ";",
        "escapechar": "\\",
    }

    header = forms.BooleanField(label=_("Header"), required=False)
    delimiter = forms.ChoiceField(label=_("Delimiter"), choices=list(zip(delimiters, delimiters)), initial=",")
    quotechar = forms.ChoiceField(label=_("Quotechar"), choices=list(zip(quotes, quotes)), initial="'")
    quoting = forms.TypedChoiceField(
        coerce=int,
        label=_("Quoting"),
        choices=(
            (csv.QUOTE_ALL, _("All")),
            (csv.QUOTE_MINIMAL, _("Minimal")),
            (csv.QUOTE_NONE, _("None")),
            (csv.QUOTE_NONNUMERIC, _("Non Numeric")),
        ),
        initial=csv.QUOTE_ALL,
    )

    escapechar = forms.ChoiceField(label=_("Escapechar"), choices=(("", ""), ("\\", "\\")), required=False)
