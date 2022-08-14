import json

from smart_register.publish.utils import wraps, unwrap
from urllib.parse import quote, unquote


def test_wrappers():
    data = json.dumps({"a": 1, "b": 22})
    wrapped = wraps(data)
    assert wrapped == '{"data": "%7B%22a%22%3A%201%2C%20%22b%22%3A%2022%7D"}'
    unwrapped = unwrap(wrapped)
    assert unwrapped == data
