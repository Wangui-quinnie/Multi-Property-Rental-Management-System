from datetime import date

from django.db.models import Sum

from ..models import Invoice
from .invoice import get_invoices_for_user


def get_overdue_invoices_queryset_for_user(user):
    """
    Returns overdue invoices (due date passed, balance outstanding)
    scoped identically to normal invoice visibility. Uses the DB-level
    approximation (due_date < today, balance > 0) rather than Python
    filtering — safe here since we need a real queryset to aggregate
    over, not just a list.
    """
    return get_invoices_for_user(user).filter(
        due_date__lt=date.today(),
        balance__gt=0,
    )


def get_arrears_by_lease(user):
    """
    Per-lease arrears summary: total outstanding balance across all
    overdue invoices for that lease, plus how many days the oldest
    unpaid invoice has been overdue.
    """
    overdue = get_overdue_invoices_queryset_for_user(user).select_related(
        "lease__tenant__user", "lease__unit__property"
    )

    by_lease = {}
    for invoice in overdue:
        lease = invoice.lease
        entry = by_lease.setdefault(lease.id, {
            "lease_id": str(lease.id),
            "tenant_name": lease.tenant.user.get_full_name(),
            "unit_number": lease.unit.unit_number,
            "property_name": lease.unit.property.name,
            "total_arrears": 0,
            "oldest_due_date": invoice.due_date,
            "overdue_invoice_count": 0,
        })
        entry["total_arrears"] += invoice.balance
        entry["overdue_invoice_count"] += 1
        if invoice.due_date < entry["oldest_due_date"]:
            entry["oldest_due_date"] = invoice.due_date

    results = list(by_lease.values())
    for entry in results:
        entry["days_in_arrears"] = (date.today() - entry["oldest_due_date"]).days

    return sorted(results, key=lambda e: e["days_in_arrears"], reverse=True)


def get_arrears_by_tenant(user):
    """
    Per-tenant arrears summary — aggregates across ALL of a tenant's
    leases, in case they have more than one (e.g. multiple units).
    """
    overdue = get_overdue_invoices_queryset_for_user(user).select_related(
        "lease__tenant__user"
    )

    by_tenant = {}
    for invoice in overdue:
        tenant = invoice.lease.tenant
        entry = by_tenant.setdefault(tenant.id, {
            "tenant_id": str(tenant.id),
            "tenant_name": tenant.user.get_full_name(),
            "total_arrears": 0,
            "overdue_invoice_count": 0,
            "leases_in_arrears": set(),
        })
        entry["total_arrears"] += invoice.balance
        entry["overdue_invoice_count"] += 1
        entry["leases_in_arrears"].add(str(invoice.lease_id))

    results = []
    for entry in by_tenant.values():
        entry["lease_count"] = len(entry["leases_in_arrears"])
        del entry["leases_in_arrears"]
        results.append(entry)

    return sorted(results, key=lambda e: e["total_arrears"], reverse=True)


def get_arrears_dashboard_for_user(user):
    by_lease = get_arrears_by_lease(user)
    by_tenant = get_arrears_by_tenant(user)

    portfolio_total = get_overdue_invoices_queryset_for_user(user).aggregate(
        total=Sum("balance")
    )["total"] or 0

    return {
        "portfolio_total_arrears": portfolio_total,
        "leases_in_arrears": len(by_lease),
        "tenants_in_arrears": len(by_tenant),
        "by_lease": by_lease,
        "by_tenant": by_tenant,
    }