from .models import Message
from ..state import state


class Dictionary:
    def __init__(self, locale):
        self.locale = locale
        self.messages = {}

    def __getitem__(self, msgid):
        translation = msgid
        try:
            translation = self.messages[msgid]
        except KeyError:
            try:
                msg = Message.objects.get(locale=self.locale, msgid=msgid, draft=False)
                translation = msg.msgstr
            except Message.DoesNotExist:
                if state.collect_messages:
                    msg, __ = Message.objects.get_or_create(msgid=msgid, locale=self.locale, defaults={"msgstr": msgid})
                    translation = msg.msgstr

        return translation


class Cache:
    def __init__(self):
        self.locales = {}

    def __getitem__(self, locale):
        try:
            entry = self.locales[locale]
        except KeyError:
            entry = Dictionary(locale)
            self.locales[locale] = entry

        return entry


cache = Cache()
del Cache
