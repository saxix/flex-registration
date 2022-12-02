import factory.fuzzy
from django.contrib.auth.models import Group, User
from factory.base import FactoryMetaClass

factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class ModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


class GroupFactory(ModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = Group
        django_get_or_create = ("name",)


class UserFactory(ModelFactory):
    username = factory.Sequence(lambda d: "username-%s" % d)
    email = factory.Faker("email")
    first_name = factory.Faker("name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = User
        django_get_or_create = ("username",)
