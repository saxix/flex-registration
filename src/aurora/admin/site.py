import logging
from django.utils.functional import lazy
from smart_admin.site import SmartAdminSite

from aurora import get_full_version

logger = logging.getLogger(__name__)


class AuroraAdminSite(SmartAdminSite):
    sysinfo_url = False
    site_title = ""
    site_header = lazy(lambda x: f"{get_full_version()}")
