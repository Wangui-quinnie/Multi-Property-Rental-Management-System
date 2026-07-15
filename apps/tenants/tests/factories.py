import factory
from factory.django import DjangoModelFactory

from apps.accounts.tests.factories import TenantUserFactory
from apps.tenants.models import Tenant


class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant

    user = factory.SubFactory(TenantUserFactory)
    national_id = factory.Sequence(lambda n: f"ID{n:06d}")
    emergency_contact_name = "Jane Doe"
    emergency_contact_phone = "0700000000"
    status = Tenant.Status.ACTIVE