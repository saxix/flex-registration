from django.db.models.signals import post_save

from smart_register.core.models import FlexFormField, FormSet


def update_cache(sender, instance, **kwargs):
    if isinstance(instance, FlexFormField):
        instance.flex_form.save()
    elif isinstance(instance, FormSet):
        instance.parent.save()


def cache_handler():
    post_save.connect(update_cache, sender=FlexFormField, dispatch_uid="field_dip")
    post_save.connect(update_cache, sender=FormSet, dispatch_uid="formset_dip")
