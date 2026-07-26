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

export type Payment = components["schemas"]["Payment"];
export type PaymentAllocation = components["schemas"]["PaymentAllocation"];
export type PaymentCreate = components["schemas"]["PaymentCreate"];

export type PaymentListParams = NonNullable<operations["payments_list"]["parameters"]["query"]> & {
  status?: "PENDING" | "CONFIRMED" | "FAILED" | "REVERSED";
  tenant?: string;
  payment_method?: "CASH" | "BANK_TRANSFER" | "MPESA" | "CARD" | "OTHER";
};
export type PaginatedPayments = components["schemas"]["PaginatedPaymentList"];

export interface AllocateToInvoicePayload {
  invoice: string;
  amount: string;
}

// Real shape of the enveloped `data` field returned by GET
// /api/payments/{id}/receipt/ (get_receipt_data in
// apps/payments/services/receipt.py). The generated schema wrongly
// claims this returns a bare Payment.
export interface ReceiptAllocationLine {
  invoice_number: string;
  unit_number: string;
  property_name: string;
  amount_allocated: string;
}

export interface Receipt {
  receipt_number: string;
  payment_reference: string;
  payment_method: string;
  payment_date: string;
  amount_paid: string;
  tenant_name: string;
  tenant_email: string;
  allocations: ReceiptAllocationLine[];
  total_allocated: string;
  unallocated_amount: string;
  notes: string;
}

export function listPayments(params?: PaymentListParams) {
  return apiClient.get<PaginatedPayments>("/payments/", { params }).then((res) => res.data);
}

export function getPayment(id: string) {
  return apiClient.get<Payment>(`/payments/${id}/`).then((res) => res.data);
}

export function createPayment(data: PaymentCreate) {
  return apiClient.post<Payment>("/payments/", data).then((res) => res.data);
}

export function allocatePaymentToInvoice(paymentId: string, data: AllocateToInvoicePayload) {
  return unwrap<Payment>(apiClient.post(`/payments/${paymentId}/allocate/`, data));
}

export function allocatePaymentToOldest(paymentId: string) {
  return unwrap<Payment>(apiClient.post(`/payments/${paymentId}/allocate-oldest/`));
}

export function removePaymentAllocation(paymentId: string, allocationId: string) {
  return unwrap<Payment>(
    apiClient.post(`/payments/${paymentId}/allocations/${allocationId}/remove/`)
  );
}

export function getReceipt(paymentId: string) {
  return unwrap<Receipt>(apiClient.get(`/payments/${paymentId}/receipt/`));
}

// Not enveloped - the backend streams a real PDF FileResponse, not JSON.
// responseType: "blob" so axios doesn't try to parse binary data as text.
export function downloadReceiptPdf(paymentId: string) {
  return apiClient
    .get(`/payments/${paymentId}/receipt/pdf/`, { responseType: "blob" })
    .then((res) => res.data as Blob);
}

export function reconcilePayment(paymentId: string) {
  return unwrap<Payment>(apiClient.post(`/payments/${paymentId}/reconcile/`));
}
