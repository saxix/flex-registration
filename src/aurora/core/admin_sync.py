from admin_extra_buttons.decorators import choice, view
from admin_sync.mixin import SyncMixin as SyncMixin_


class SyncMixin(SyncMixin_):
    @choice(order=900, change_list=False)
    def admin_sync(self, button):
        button.choices = [
            self._admin_sync_inspect,
            self._sync,
            self._publish,
        ]
        return button

    @view(change_form=True)
    def _admin_sync_inspect(self, request, pk):
        return self.admin_sync_inspect.func(self, request, pk)

    @view(change_form=True)
    def _sync(self, request, pk):
        return self.sync.func(self, request, pk)

    @view(change_form=True)
    def _publish(self, request, pk):
        return self.publish.func(self, request, pk)

    def get_changeform_buttons(self, context):
        ignored = ["admin_sync_inspect", "sync", "publish"]
        return [
            h for h in self.extra_button_handlers.values() if h.change_form in [True, None] and h.name not in ignored
        ]
