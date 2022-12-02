from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db import IntegrityError


class AnyUserAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if settings.DEBUG and request.get_host().startswith("localhost"):
            try:
                user, __ = User.objects.update_or_create(
                    username=username, is_staff=True, is_active=True, is_superuser=True, email=f"{username}@demo.org"
                )
                user.set_password(password)
                user.save()
                return user
            except (User.DoesNotExist, IntegrityError):
                pass
