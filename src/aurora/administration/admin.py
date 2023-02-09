from admin_extra_buttons.decorators import button
from adminactions.helpers import AdminActionPermMixin
from hijack.templatetags.hijack import can_hijack
from smart_admin.smart_auth.admin import GroupAdmin, UserAdmin

from aurora.administration.hijack import impersonate
from aurora.core.admin_sync import SyncMixin
from aurora.core.utils import is_root


class AuroraUserAdmin(AdminActionPermMixin, UserAdmin):
    @button(permission=lambda req, obj, **kw: is_root(req) and can_hijack(req.user, obj))
    def hijack(self, request, pk):
        hijacked = self.get_object(request, pk)
        impersonate(request, hijacked)


class AuroraGroupAdmin(AdminActionPermMixin, SyncMixin, GroupAdmin):
    pass
