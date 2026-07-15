import factory
from factory.django import DjangoModelFactory

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.models import Property, Unit


class PropertyFactory(DjangoModelFactory):
    class Meta:
        model = Property

    landlord = factory.SubFactory(LandlordUserFactory)
    name = factory.Sequence(lambda n: f"Property {n}")
    code = factory.Sequence(lambda n: f"PROP{n:04d}")
    location = "Nairobi"
    address = "Test Address"
    status = Property.Status.ACTIVE


class UnitFactory(DjangoModelFactory):
    class Meta:
        model = Unit

    property = factory.SubFactory(PropertyFactory)
    unit_number = factory.Sequence(lambda n: f"U{n:03d}")
    unit_type = "1 Bedroom"
    floor_number = 1
    rent_amount = 25000
    status = Unit.Status.VACANT