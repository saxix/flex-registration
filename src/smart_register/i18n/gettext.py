from django.conf import settings
from django.utils.safestring import SafeData, mark_safe
from django.utils.translation.trans_real import translation, _active, DjangoTranslation, _default


def gettext(message):
    """
    Translate the 'message' string. It uses the current thread to find the
    translation object to use. If no current translation is activated, the
    message will be run through the default translation object.
    """
    global _default

    eol_message = message.replace("\r\n", "\n").replace("\r", "\n")

    if eol_message:
        _default = _default or translation(settings.LANGUAGE_CODE)
        translation_object = getattr(_active, "value", _default)
        # FIXME: remove me (print)
        print(111, "gettext.py:20 (gettext)", 11111111, message)
        # # CANICOMPET
        # if (
        #     type(translation_object) == DjangoTranslation
        #     and translation_object.language() in settings.LANGUAGE_TO_GOOGLE_CODES
        # ):
        #     result = settings.LANGUAGE_TO_GOOGLE_FCT(eol_message, translation_object.language())
        # else:
        #     # original Django
        result = translation_object.gettext(eol_message)

    else:
        # Return an empty value of the corresponding type if an empty message
        # is given, instead of metadata, which is the default gettext behavior.
        result = type(message)("")

    if isinstance(message, SafeData):
        return mark_safe(result)

    return result
