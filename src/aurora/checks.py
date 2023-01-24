import os

from django.core.checks import Error, register


@register("aurora", "env")
def check_env_setting(app_configs, **kwargs):
    errors = []
    from .config import MANDATORY

    for entry, __ in MANDATORY.items():
        if entry not in os.environ:
            errors.append(
                Error(
                    f"{entry} environment variable is not set",
                    # hint=f"set '{entry}' environment variable",
                    obj="os.environ",
                    id="aurora.ENV",
                )
            )
    return errors
