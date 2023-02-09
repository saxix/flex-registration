from typing import Iterable

from admin_sync.collector import ForeignKeysCollector
from admin_sync.exceptions import SyncError
from admin_sync.protocol import LoadDumpProtocol


class AuroraSyncProjectProtocol(LoadDumpProtocol):
    def collect(self, data: Iterable, collect_related=True):
        from aurora.core.models import Project

        if len(data) == 0:
            raise SyncError("Empty queryset")  # pragma: no cover

        if not isinstance(data[0], Project):  # pragma: no cover
            raise ValueError("AuroraSyncProjectProtocol can be used only for Project")
        return_value = []
        for o in list(data):
            c = ForeignKeysCollector(False)
            c.collect([o])
            return_value.extend(c.data)
        return return_value


class AuroraSyncOrganizationProtocol(LoadDumpProtocol):
    def collect(self, data: Iterable, collect_related=True):
        from aurora.core.models import Organization

        if len(data) == 0:
            raise SyncError("Empty queryset")  # pragma: no cover

        if not isinstance(data[0], Organization):  # pragma: no cover
            raise ValueError("AuroraSyncOrganizationProtocol can be used only for Organization")
        return_value = []
        for o in list(data):
            c = ForeignKeysCollector(False)
            c.collect([o])
            return_value.extend(c.data)
        return return_value
