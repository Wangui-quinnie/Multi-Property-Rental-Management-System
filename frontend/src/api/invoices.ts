import { apiClient } from "./client";
import type { components, operations } from "@/types/api";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(promise: Promise<{ data: Envelope<T> }>): Promise<T> {
  return promise.then((res) => res.data.data);
}

export type Invoice = components["schemas"]["Invoice"];
export type InvoiceItem = components["schemas"]["InvoiceItem"];

export type InvoiceListParams = NonNullable<
  operations["billing_invoices_list"]["parameters"]["query"]
> & {
  status?: "DRAFT" | "UNPAID" | "PARTIALLY_PAID" | "PAID" | "OVERDUE" | "CANCELLED";
  billing_period?: string;
  lease?: string;
};
export type PaginatedInvoices = components["schemas"]["PaginatedInvoiceList"];

export interface GenerateRentInvoicesPayload {
  billing_period: string;
}

export interface ApplyLateFeePayload {
  fee_type: "FIXED" | "PERCENTAGE";
  value: string;
}

export interface ApplyLateFeesBatchPayload {
  billing_period: string;
  fee_type: "FIXED" | "PERCENTAGE";
  value: string;
}

// Real shape of the enveloped `data` field returned by GET
// /api/billing/invoices/arrears/ (get_arrears_dashboard_for_user in
// apps/billing/selectors/arrears.py). Decimal fields (total_arrears,
// portfolio_total_arrears) serialize as strings, same as every other
// Decimal field in this API (e.g. Lease.rent_amount).
export interface ArrearsByLease {
  lease_id: string;
  tenant_name: string;
  unit_number: string;
  property_name: string;
  total_arrears: string;
  oldest_due_date: string;
  overdue_invoice_count: number;
  days_in_arrears: number;
}

export interface ArrearsByTenant {
  tenant_id: string;
  tenant_name: string;
  total_arrears: string;
  overdue_invoice_count: number;
  lease_count: number;
}

export interface ArrearsDashboard {
  portfolio_total_arrears: string;
  leases_in_arrears: number;
  tenants_in_arrears: number;
  by_lease: ArrearsByLease[];
  by_tenant: ArrearsByTenant[];
}

export function listInvoices(params?: InvoiceListParams) {
  return apiClient.get<PaginatedInvoices>("/billing/invoices/", { params }).then((res) => res.data);
}

export function getInvoice(id: string) {
  return apiClient.get<Invoice>(`/billing/invoices/${id}/`).then((res) => res.data);
}

export function generateRentInvoices(data: GenerateRentInvoicesPayload) {
  return unwrap<Invoice[]>(apiClient.post("/billing/invoices/generate-rent/", data));
}

export function applyLateFee(invoiceId: string, data: ApplyLateFeePayload) {
  return unwrap<Invoice>(apiClient.post(`/billing/invoices/${invoiceId}/apply-late-fee/`, data));
}

export function applyLateFeesBatch(data: ApplyLateFeesBatchPayload) {
  return unwrap<{ late_fees_applied: number }>(
    apiClient.post("/billing/invoices/apply-late-fees/", data)
  );
}

export function markOverdueInvoices() {
  return unwrap<{ invoices_marked_overdue: number }>(
    apiClient.post("/billing/invoices/mark-overdue/")
  );
}

export function getArrearsDashboard() {
  return unwrap<ArrearsDashboard>(apiClient.get("/billing/invoices/arrears/"));
}
