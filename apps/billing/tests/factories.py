import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta

from apps.billing.models import BillingPeriod


class BillingPeriodFactory(DjangoModelFactory):
    class Meta:
        model = BillingPeriod

    name = factory.Sequence(lambda n: f"Billing Period {n}")
    start_date = factory.Sequence(lambda n: date(2026, 1, 1) + timedelta(days=32 * n))
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=29))
    due_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=5))
    status = BillingPeriod.Status.OPEN