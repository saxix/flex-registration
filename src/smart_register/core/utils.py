import base64
import datetime
import decimal
import io
import json
import re
import time
import unicodedata
from collections import deque
from itertools import chain
from pathlib import Path
from sys import getsizeof, stderr

import qrcode
from constance import config
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files.utils import FileProxyMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template import loader
from django.utils.functional import keep_lazy_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import is_aware

from smart_register import VERSION
from smart_register.state import state

UNDEFINED = object()


def has_token(request, *args, **kwargs):
    return (request.headers.get("x-session") == settings.ROOT_TOKEN
            or request.COOKIES.get("x-session") == settings.ROOT_TOKEN)


def is_root(request, *args, **kwargs):
    return request.user.is_superuser and has_token(request)


@keep_lazy_text
def namify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return slugify(re.sub(r"[-\s]+", "_", value).strip("-_"))


class JSONEncoder(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    def __init__(self, **kwargs):
        self.skip_files = kwargs.pop("skip_files", False)
        super().__init__(**kwargs)

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, FileProxyMixin):
            if self.skip_files:
                return "::file::"
            else:
                o.seek(0)
                data = o.read()
                return data
        elif isinstance(o, memoryview):
            return base64.urlsafe_b64encode(o.tobytes())
        elif isinstance(o, bytes):
            return str(o, encoding="utf-8")
            # return base64.encodebytes(o)
        elif isinstance(o, Exception):
            return str(o)
        else:
            return super().default(o)


def safe_json(data):
    return json.dumps(data, cls=JSONEncoder)


def jsonfy(data):
    return json.loads(safe_json(data))


def underscore_to_camelcase(value):
    return value[0].upper() + "".join(
        list(
            map(
                lambda index_word: index_word[1].lower()
                if index_word[0] == 0
                else index_word[1][0].upper() + (index_word[1][1:] if len(index_word[1]) > 0 else ""),
                list(enumerate(re.split(re.compile(r"[_ ]+"), value[1:]))),
            )
        )
    )


def render(request, template_name, context=None, content_type=None, status=None, using=None, cookies=None):
    """
    Return a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    content = loader.render_to_string(template_name, context, request, using=using)
    response = HttpResponse(content, content_type, status)
    if cookies:
        for k, v in cookies.items():
            response.set_cookie(k, v)

    return response


def clean(v):
    return v.replace(r"\n", "").strip()


def get_bookmarks(request):
    quick_links = []
    for entry in config.SMART_ADMIN_BOOKMARKS.split("\n"):
        if entry := clean(entry):
            try:
                if entry == "--":
                    quick_links.append(mark_safe("<li><hr/></li>"))
                elif entry.startswith("#"):
                    quick_links.append(mark_safe(f"<li>{entry[1:]}</li>"))
                elif parts := entry.split(","):
                    args = None
                    if len(parts) == 1:
                        args = parts[0], "viewlink", parts[0], parts[0]
                    elif len(parts) == 2:
                        args = parts[0], "viewlink", parts[1], parts[0]
                    elif len(parts) == 3:
                        args = parts[0], "viewlink", parts[1], parts[0]
                    elif len(parts) == 4:
                        args = parts.reverse()
                    if args:
                        quick_links.append(format_html('<li><a target="{}" class="{}" href="{}">{}</a></li>', *args))
            except ValueError:
                pass
    return quick_links


def get_qrcode(content):
    logo_link = Path(settings.BASE_DIR) / "web/static/unicef_logo.jpeg"
    from PIL import Image

    logo = Image.open(logo_link)
    basewidth = 100
    wpercent = basewidth / float(logo.size[0])
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    QRcode.add_data(content)
    QRcode.make()
    QRimg = QRcode.make_image(fill_color="black", back_color="white").convert("RGB")

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)
    buff = io.BytesIO()
    # save the QR code generated
    QRimg.save(buff, format="PNG")
    return base64.b64encode(buff.getvalue()).decode()


def dict_setdefault(source: dict, d: dict):
    for k, v in d.items():
        if isinstance(v, dict):
            source.setdefault(k, v)
            dict_setdefault(source[k], v)
        else:
            source.setdefault(k, v)
    return source


def dict_get_nested(obj: dict, path):
    parts = path.split(".")
    current = obj
    for p in parts:
        if p not in current:
            current[p] = {}
        current = current[p]
    return current


def clone_model(source, **kwargs):
    if obj := source.__class__.objects.filter(**kwargs).first():
        return obj, False
    obj = source.__class__.objects.get(pk=source.pk)

    obj.pk = None
    for k, v in kwargs.items():
        setattr(obj, k, v)
    obj.save()
    return obj, True


def clone_form(instance, **kwargs):
    cloned = clone_model(instance, **kwargs)
    for field in instance.fields.all():
        field.pk = None
        field.flex_form = cloned
        field.save()
    return cloned


def get_client_ip(request):
    """
    type: (WSGIRequest) -> Optional[Any]
    Naively yank the first IP address in an X-Forwarded-For header
    and assume this is correct.

    Note: Don't use this in security sensitive situations since this
    value may be forged from a client.
    """
    if request:
        for x in [
            "HTTP_X_ORIGINAL_FORWARDED_FOR",
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_REAL_IP",
            "REMOTE_ADDR",
        ]:
            ip = request.META.get(x)
            if ip:
                return ip.split(",")[0].strip()


def get_versioned_static_name(name):
    return name


def get_etag(request, *args, **kwargs):
    if state.collect_messages:
        params = [time.time()]
    else:
        params = (VERSION,) + args
    return "/".join(map(str, params))


def last_day_of_month(date):
    return date.replace(day=1) + relativedelta(months=1) - relativedelta(days=1)


def apply_nested(cleaned_value, func=lambda v, k: v, key=None):
    # if isinstance(cleaned_value, FileProxyMixin):
    #     return base64.b64encode(cleaned_value.read())
    if isinstance(cleaned_value, dict):
        return {item[0]: apply_nested(item[1], func, item[0]) for item in cleaned_value.items()}
    elif isinstance(cleaned_value, list):
        return [apply_nested(item, func, key) for item in cleaned_value]
    # elif cleaned_value is None:
    #     cleaned_value = ""
    return func(cleaned_value, key)


def extract_content(r):
    return apply_nested(r, lambda k, v: v.read() if isinstance(v, FileProxyMixin) else v)


def merge_data(d1, d2):
    if isinstance(d2, dict):
        ret = {} or d1.copy()
        for k, v in d2.items():
            if isinstance(v, list):
                if k not in d1:
                    d1[k] = [None for e in v]
                ret[k] = [merge_data(d1[k][i], e) for i, e in enumerate(v)]
            elif isinstance(v, dict):
                if k not in d1:
                    d1[k] = {}
                ret[k] = merge_data(d1[k], v)
            else:
                ret[k] = d2[k]
        return ret
    else:
        return d2


def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                    }
    all_handlers.update(handlers)  # user handlers take precedence
    seen = set()  # track which object id's have already been seen
    default_size = getsizeof(0)  # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:  # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)
