from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce, TruncMonth

from apps.billing.models import Invoice, InvoiceItem
from apps.billing.selectors import get_invoices_for_user, get_arrears_dashboard_for_user
from apps.payments.models import Payment
from apps.payments.selectors import get_payments_for_user
from apps.properties.selectors import get_properties_for_user, get_portfolio_summary_for_user
from apps.vacancy.selectors import get_vacancy_dashboard_for_user


def get_rent_billed_vs_collected(user, start_date=None, end_date=None):
    """
    Rent BILLED is precise — InvoiceItem.item_type=RENT is an exact
    fact recorded at invoice-generation time. Collected is reported
    as one combined total (rent + any other charges on the same
    invoices), NOT split by category — a Payment is allocated
    per-invoice, not per-line-item, so a rent/water split on the
    collected side would be a fabricated approximation, not a fact.
    """
    invoices = get_invoices_for_user(user)
    if start_date:
        invoices = invoices.filter(invoice_date__gte=start_date)
    if end_date:
        invoices = invoices.filter(invoice_date__lte=end_date)

    rent_billed = InvoiceItem.objects.filter(
        invoice__in=invoices, item_type=InvoiceItem.ItemType.RENT
    ).aggregate(total=Coalesce(Sum("amount"), Decimal("0")))["total"]

    total_billed = invoices.aggregate(total=Coalesce(Sum("total_amount"), Decimal("0")))["total"]
    total_collected = invoices.aggregate(total=Coalesce(Sum("amount_paid"), Decimal("0")))["total"]
    total_outstanding = invoices.aggregate(total=Coalesce(Sum("balance"), Decimal("0")))["total"]

    return {
        "rent_billed": rent_billed,
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_outstanding": total_outstanding,
        "invoice_count": invoices.count(),
    }


def get_water_billing_summary(user, start_date=None, end_date=None):
    """
    Billed only — see get_rent_billed_vs_collected's docstring for
    why a "water collected" figure isn't reported as a precise number.
    """
    from apps.billing.selectors import get_water_readings_for_user

    readings = get_water_readings_for_user(user)
    if start_date:
        readings = readings.filter(reading_date__gte=start_date)
    if end_date:
        readings = readings.filter(reading_date__lte=end_date)

    summary = readings.aggregate(
        total_units_consumed=Coalesce(Sum("units_consumed"), Decimal("0")),
        total_water_billed=Coalesce(Sum("amount"), Decimal("0")),
    )
    summary["reading_count"] = readings.count()
    return summary


def get_cash_flow_trend(user, months=6):
    """
    Confirmed payment totals grouped by month, most recent `months`
    worth. A simple revenue trend line, not itemized by category —
    same reasoning as above.
    """
    payments = get_payments_for_user(user).filter(status=Payment.Status.CONFIRMED)

    trend = (
        payments.annotate(month=TruncMonth("payment_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("-month")[:months]
    )

    return [
        {"month": entry["month"].strftime("%Y-%m"), "total_collected": entry["total"]}
        for entry in trend
    ]


def get_landlord_summary(user, start_date=None, end_date=None):
    """
    The consolidated report — combines occupancy, vacancy, arrears,
    rent/billing, water, and cash flow into one response. Each
    section reuses the same selector that powers its own dedicated
    dashboard elsewhere in the API, so numbers can never drift
    between "the summary" and "the detailed view."
    """
    return {
        "occupancy": get_portfolio_summary_for_user(user),
        "vacancy": get_vacancy_dashboard_for_user(user),
        "arrears": get_arrears_dashboard_for_user(user),
        "rent": get_rent_billed_vs_collected(user, start_date=start_date, end_date=end_date),
        "water": get_water_billing_summary(user, start_date=start_date, end_date=end_date),
        "cash_flow": get_cash_flow_trend(user),
    }