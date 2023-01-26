from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone

from aurora.registration.models import Registration


class RegistrationRole(models.Model):
    registration = models.ForeignKey(Registration, related_name="roles", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Group, on_delete=models.CASCADE)
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(default=None, null=True)

    class Meta:
        unique_together = (("registration", "user", "role"),)
