import io
import tempfile
from pathlib import Path

from django.core.management import call_command


def test_sync(db):
    buf = io.StringIO()
    workdir = Path(".").absolute()

    with tempfile.NamedTemporaryFile("w", dir=workdir, prefix="~SYNC", suffix=".json", delete=False) as fdst:
        call_command("dumpdata", "core", stdout=buf, use_natural_foreign_keys=True, use_natural_primary_keys=True)
        fdst.write(buf.getvalue())
    call_command("loaddata", (workdir / fdst.name).absolute())
