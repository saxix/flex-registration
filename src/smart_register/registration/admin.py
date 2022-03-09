from admin_extra_buttons.decorators import button
from cryptography.hazmat.primitives import serialization
from django.shortcuts import render
from import_export import resources

from django.contrib.admin import register
from import_export.admin import ImportExportMixin
from smart_admin.modeladmin import SmartModelAdmin

from .models import Registration, Record


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration


@register(Registration)
class RegistrationAdmin(ImportExportMixin, SmartModelAdmin):
    @button()
    def generate_keys(self, request, pk):
        ctx = self.get_common_context(request, pk)
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        ctx["private_key"] = private_pem
        ctx["public_key"] = public_pem

        return render(request, "admin/registration/registration/keys.html", ctx)


@register(Record)
class RecordAdmin(SmartModelAdmin):
    pass
