import factory
from factory.django import DjangoModelFactory
from django.utils import timezone

from apps.tenants.tests.factories import TenantFactory
from apps.payments.models import Payment


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    tenant = factory.SubFactory(TenantFactory)
    payment_reference = factory.Sequence(lambda n: f"PAY-{n:06d}")
    payment_method = Payment.Method.CASH
    amount = 20000
    payment_date = factory.LazyFunction(timezone.now)
    status = Payment.Status.CONFIRMED