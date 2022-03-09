from admin_extra_buttons.decorators import view
from cryptography.hazmat.primitives import serialization
from django import forms
from django.contrib import messages
from django.db import models
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
    formfield_overrides = {models.TextField: {"widget": forms.PasswordInput}}
    exclude = ("public_key",)
    change_form_template = None

    @view()
    def removekey(self, request, pk):
        self.object = self.get_object(request, pk)
        self.object.public_key = ""
        self.object.save()
        self.message_user(request, "Encryption key removed", messages.WARNING)

    @view()
    def generate_keys(self, request, pk):
        ctx = self.get_common_context(
            request, pk, title="Generate Private/Public Key pair to encrypt this Registration data"
        )
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa

        if request.method == "POST":
            ctx["title"] = "Key Pair Generated"
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
            public_key = private_key.public_key()

            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self.object.public_key = public_pem
            self.object.save()
            ctx["private_key"] = private_pem
            ctx["public_key"] = public_pem

        return render(request, "admin/registration/registration/keys.html", ctx)


@register(Record)
class RecordAdmin(SmartModelAdmin):
    pass
