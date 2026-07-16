import factory
from factory.django import DjangoModelFactory

from apps.properties.tests.factories import UnitFactory
from apps.tenants.tests.factories import TenantFactory
from apps.leases.models import Lease


class LeaseFactory(DjangoModelFactory):
    class Meta:
        model = Lease

    tenant = factory.SubFactory(TenantFactory)
    unit = factory.SubFactory(UnitFactory)
    lease_start_date = "2026-01-01"
    lease_end_date = None
    rent_amount = 25000
    deposit_amount = 25000
    billing_day = 1
    status = Lease.Status.ACTIVE