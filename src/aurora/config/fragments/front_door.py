from .. import env

FRONT_DOOR_CONFIG = "front_door.conf.DjangoConstance"
FRONT_DOOR_ENABLED = env("FRONT_DOOR_ENABLED")
FRONT_DOOR_ALLOWED_PATHS = env("FRONT_DOOR_ALLOWED_PATHS")
FRONT_DOOR_TOKEN = env("FRONT_DOOR_TOKEN")
FRONT_DOOR_HEADER = "x-aurora"
FRONT_DOOR_COOKIE_NAME = "x-aurora"
FRONT_DOOR_COOKIE_PATTERN = ".*"
# FRONT_DOOR_ERROR_CODE = 404
# FRONT_DOOR_REDIR_URL = "https://www.sosbob.com/"
FRONT_DOOR_LOG_LEVEL = env("FRONT_DOOR_LOG_LEVEL")  # LOG_RULE_FAIL
FRONT_DOOR_RULES = [
    # "front_door.rules.internal_ip",  # grant access to settings.INTERNAL_IPS
    # "front_door.rules.forbidden_path",  # DENY access to FORBIDDEN_PATHS
    "front_door.rules.allowed_path",  # grant access to ALLOWED_PATHS
    "front_door.rules.allowed_ip",  # grant access to ALLOWED_IPS
    "front_door.rules.special_header",  # grant access if request has Header[HEADER] == TOKEN
    # "front_door.rules.has_header",  # grant access if request has HEADER
    "front_door.rules.cookie_value",  # grant access if request.COOKIES[COOKIE_NAME]
    # "front_door.rules.cookie_exists",  # grant access ir COOKIE_NAME in request.COOKIES
]