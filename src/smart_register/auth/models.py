from django.contrib.auth.models import User, Group
from django.db import models

from smart_register.registration.models import Registration


class RegistrationRole(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Group, on_delete=models.CASCADE)
