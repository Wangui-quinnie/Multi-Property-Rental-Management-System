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

export type MpesaTransaction = components["schemas"]["MpesaTransaction"];

export type MpesaTransactionListParams = NonNullable<
  operations["payments_mpesa_transactions_list"]["parameters"]["query"]
> & {
  status?: "PENDING" | "SUCCESS" | "FAILED" | "CANCELLED";
  tenant?: string;
};
export type PaginatedMpesaTransactions = components["schemas"]["PaginatedMpesaTransactionList"];

export interface InitiateStkPushPayload {
  tenant: string;
  phone_number: string;
  amount: string;
}

export function listMpesaTransactions(params?: MpesaTransactionListParams) {
  return apiClient
    .get<PaginatedMpesaTransactions>("/payments/mpesa/transactions/", { params })
    .then((res) => res.data);
}

export function getMpesaTransaction(id: string) {
  return apiClient
    .get<MpesaTransaction>(`/payments/mpesa/transactions/${id}/`)
    .then((res) => res.data);
}

// Real M-Pesa confirmation arrives later via the (unauthenticated,
// server-only) callback endpoint - this only starts the STK Push and
// returns a PENDING transaction. The frontend never calls the callback
// itself; the transaction's status/payment fields update once
// process_stk_callback() runs, so poll/refetch to see the outcome.
export function initiateStkPush(data: InitiateStkPushPayload) {
  return unwrap<MpesaTransaction>(
    apiClient.post("/payments/mpesa/transactions/initiate/", data)
  );
}
