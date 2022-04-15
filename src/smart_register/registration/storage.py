import base64

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.utils import FileProxyMixin

from smart_register.core.utils import apply_nested, merge_data


def clean_dict(d, filter_func):
    ret = {}
    for key, value in d.items():
        if filter_func(value):
            pass
        elif isinstance(value, dict):
            ret[key] = clean_dict(value, filter_func)
        elif isinstance(value, list):
            ret[key] = [clean_dict(e, filter_func) for e in value]
        else:
            ret[key] = value
    return ret


class Router:
    def compress(self, fields, files):
        ff = apply_nested(files, lambda v, k: SimpleUploadedFile(k, v if isinstance(v, bytes) else v.encode()))
        return merge_data(fields, ff)

    def decompress(self, data):
        marker = object()

        files_exclude = lambda v, k: "::file::" if isinstance(v, FileProxyMixin) else v
        files_keep = lambda v, k: base64.b64encode(v.read()) if isinstance(v, FileProxyMixin) else marker

        fields = {field_name: apply_nested(field, files_exclude) for field_name, field in data.items()}
        files = {field_name: apply_nested(field, files_keep) for field_name, field in data.items()}

        files = clean_dict(files, lambda x: x == marker)
        return fields, files


router = Router()
