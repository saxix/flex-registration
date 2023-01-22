import factory.fuzzy
from django import forms
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, User
from factory.base import FactoryMetaClass
from rest_framework.authtoken.models import TokenProxy
from social_django.models import UserSocialAuth, Nonce, Association

import dbtemplates.models as dbtemplates
from aurora.core.models import FlexForm, CustomFieldType, FlexFormField
from aurora.counters.models import Counter
from aurora.registration.models import Registration, Record

factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class AutoRegisterModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


def get_factory_for_model(_model):
    class Meta:
        model = _model

    if _model in factories_registry:
        return factories_registry[_model]
    return type(f"{_model._meta.model_name}Factory", (AutoRegisterModelFactory,), {"Meta": Meta})


class GroupFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = Group
        django_get_or_create = ("name",)


class UserFactory(AutoRegisterModelFactory):
    username = factory.Sequence(lambda d: "username-%s" % d)
    email = factory.Faker("email")
    first_name = factory.Faker("name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = User
        django_get_or_create = ("username",)


class SuperUserFactory(UserFactory):
    username = factory.Sequence(lambda n: "superuser%03d@example.com" % n)
    email = factory.Sequence(lambda n: "superuser%03d@example.com" % n)
    is_superuser = True
    is_staff = True
    is_active = True


class FormFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda d: "Form-%s" % d)

    class Meta:
        model = FlexForm
        django_get_or_create = ("name",)


class FlexFormFieldFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda d: "FormField-%s" % d)
    field_type = "forms.CharField"

    class Meta:
        model = FlexFormField
        django_get_or_create = ("name",)


class CustomFieldTypeFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda d: "CustomField-%s" % d)
    base_type = forms.CharField

    class Meta:
        model = CustomFieldType
        django_get_or_create = ("name",)


class RegistrationFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda d: "Registration-%s" % d)
    title = factory.Sequence(lambda d: "Registration-%s" % d)
    slug = factory.Sequence(lambda d: "registration-%s" % d)
    flex_form = factory.SubFactory(FormFactory)

    class Meta:
        model = Registration
        django_get_or_create = ("slug",)


class RecordFactory(AutoRegisterModelFactory):
    registration = factory.SubFactory(RegistrationFactory)

    class Meta:
        model = Record


class CounterFactory(AutoRegisterModelFactory):
    registration = factory.SubFactory(RegistrationFactory)
    details = {"hours": {str(x): 10 for x in range(23)}}

    class Meta:
        model = Counter


class LogEntryFactory(AutoRegisterModelFactory):
    action_flag = 1
    user = factory.SubFactory(UserFactory, username="admin")

    class Meta:
        model = LogEntry


class TokenProxyFactory(AutoRegisterModelFactory):
    user = factory.SubFactory(UserFactory, username="admin")

    class Meta:
        model = TokenProxy


class UserSocialAuthFactory(AutoRegisterModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = UserSocialAuth


class NonceFactory(AutoRegisterModelFactory):
    timestamp = 1

    class Meta:
        model = Nonce


class AssociationFactory(AutoRegisterModelFactory):
    issued = 1
    lifetime = 1

    class Meta:
        model = Association


class TemplateFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda d: "Template-%s" % d)
    content = ""

    class Meta:
        model = dbtemplates.Template
