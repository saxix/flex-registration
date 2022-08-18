from django.contrib.auth.backends import ModelBackend


class SmartBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_active and super().has_perm(user_obj, perm, obj=obj)
