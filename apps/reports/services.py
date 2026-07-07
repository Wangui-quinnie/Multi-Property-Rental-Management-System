from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum
from django.db.models.functions import Coalesce

from apps.billing.models import Invoice, InvoiceItem, WaterMeterReading
from apps.payments.models import Payment
from apps.properties.models import Property, Unit


def get_rent_collection_summary(start_date=None, end_date=None, property_id=None):
    payments = Payment.objects.filter(
        status=Payment.Status.CONFIRMED
    )

    if start_date:
        payments = payments.filter(payment_date__date__gte=start_date)

    if end_date:
        payments = payments.filter(payment_date__date__lte=end_date)

    if property_id:
        payments = payments.filter(
            tenant__leases__unit__property_id=property_id
        ).distinct()

    total_collected = payments.aggregate(
        total=Coalesce(Sum("amount"), Decimal("0"), output_field=DecimalField())
    )["total"]

    return {
        "total_collected": total_collected,
        "payment_count": payments.count(),
    }


def get_arrears_summary(property_id=None):
    invoices = Invoice.objects.filter(
        status__in=[
            Invoice.Status.UNPAID,
            Invoice.Status.PARTIALLY_PAID,
            Invoice.Status.OVERDUE,
        ]
    )

    if property_id:
        invoices = invoices.filter(
            lease__unit__property_id=property_id
        )

    total_arrears = invoices.aggregate(
        total=Coalesce(Sum("balance"), Decimal("0"), output_field=DecimalField())
    )["total"]

    tenants_in_arrears = invoices.values(
        "lease__tenant"
    ).distinct().count()

    return {
        "total_arrears": total_arrears,
        "tenants_in_arrears": tenants_in_arrears,
    }


def get_occupancy_summary(property_id=None):
    units = Unit.objects.all()

    if property_id:
        units = units.filter(property_id=property_id)

    summary = units.aggregate(
        total_units=Count("id"),
        occupied_units=Count("id", filter=Q(status=Unit.Status.OCCUPIED)),
        vacant_units=Count("id", filter=Q(status=Unit.Status.VACANT)),
        maintenance_units=Count("id", filter=Q(status=Unit.Status.MAINTENANCE)),
    )

    total_units = summary["total_units"] or 0
    occupied_units = summary["occupied_units"] or 0

    occupancy_rate = 0
    if total_units:
        occupancy_rate = round((occupied_units / total_units) * 100, 2)

    summary["occupancy_rate"] = occupancy_rate

    return summary


def get_water_billing_summary(start_date=None, end_date=None, property_id=None):
    readings = WaterMeterReading.objects.all()

    if start_date:
        readings = readings.filter(reading_date__gte=start_date)

    if end_date:
        readings = readings.filter(reading_date__lte=end_date)

    if property_id:
        readings = readings.filter(unit__property_id=property_id)

    summary = readings.aggregate(
        total_units_consumed=Coalesce(
            Sum("units_consumed"), Decimal("0"), output_field=DecimalField()
        ),
        total_water_billed=Coalesce(
            Sum("amount"), Decimal("0"), output_field=DecimalField()
        ),
    )

    summary["reading_count"] = readings.count()

    return summary


def get_property_income_summary(property_id=None):
    properties = Property.objects.all()

    if property_id:
        properties = properties.filter(id=property_id)

    data = []

    for property_obj in properties:
        invoices = Invoice.objects.filter(
            lease__unit__property=property_obj
        ).exclude(
            status=Invoice.Status.CANCELLED
        )

        payments = Payment.objects.filter(
            tenant__leases__unit__property=property_obj,
            status=Payment.Status.CONFIRMED,
        ).distinct()

        data.append({
            "property": property_obj,
            "total_billed": invoices.aggregate(
                total=Coalesce(Sum("total_amount"), Decimal("0"), output_field=DecimalField())
            )["total"],
            "total_paid": payments.aggregate(
                total=Coalesce(Sum("amount"), Decimal("0"), output_field=DecimalField())
            )["total"],
            "total_balance": invoices.aggregate(
                total=Coalesce(Sum("balance"), Decimal("0"), output_field=DecimalField())
            )["total"],
            "unit_count": property_obj.units.count(),
        })

    return data