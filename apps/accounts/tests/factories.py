import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = "Test"
    last_name = "User"
    role = User.Role.TENANT

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "TestPass123!")
        user = model_class(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class AdminUserFactory(UserFactory):
    role = User.Role.ADMIN


class LandlordUserFactory(UserFactory):
    role = User.Role.LANDLORD


class TenantUserFactory(UserFactory):
    role = User.Role.TENANT