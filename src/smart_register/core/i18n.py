from django.utils.translation.trans_real import DjangoTranslation
from django.views.i18n import JavaScriptCatalog

LANGUAGE_QUERY_PARAMETER = "language"


class SmartJavascriptCatalog(JavaScriptCatalog):
    domain = "djangojs"
    packages = None

    def get(self, request, *args, **kwargs):
        locale = self.kwargs["locale"]
        domain = kwargs.get("domain", self.domain)
        # If packages are not provided, default to all installed packages, as
        # DjangoTranslation without localedirs harvests them all.
        packages = kwargs.get("packages", "")
        packages = packages.split("+") if packages else self.packages
        paths = self.get_paths(packages) if packages else None
        self.translation = DjangoTranslation(locale, domain=domain, localedirs=paths)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
