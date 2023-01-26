from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.utils import timezone

from .models import OrganizationRole, RegistrationRole


class SmartBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        from aurora.registration.models import Registration

        if obj and isinstance(obj, Registration):
            app_label, perm_name = perm.split(".")
            return (
                RegistrationRole.objects.filter(
                    user=user_obj,
                    role__permissions__codename=perm_name,
                    role__permissions__content_type__app_label=app_label,
                )
                .filter(valid_from__lte=timezone.now())
                .filter(Q(valid_until__gte=timezone.now()) | Q(valid_until__isnull=True))
                .exists()
            )

        return user_obj.is_active and super().has_perm(user_obj, perm, obj=obj)


class OrganizationBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        from aurora.registration.models import Registration

        if obj and isinstance(obj, Registration):
            app_label, perm_name = perm.split(".")
            return (
                OrganizationRole.objects.filter(
                    user=user_obj,
                    role__permissions__codename=perm_name,
                    role__permissions__content_type__app_label=app_label,
                )
                .filter(valid_from__lte=timezone.now())
                .filter(Q(valid_until__gte=timezone.now()) | Q(valid_until__isnull=True))
                .exists()
            )

        return user_obj.is_active and super().has_perm(user_obj, perm, obj=obj)
