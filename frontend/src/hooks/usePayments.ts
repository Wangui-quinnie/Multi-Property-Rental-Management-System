import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  allocatePaymentToInvoice,
  allocatePaymentToOldest,
  createPayment,
  downloadReceiptPdf,
  getPayment,
  getReceipt,
  listPayments,
  reconcilePayment,
  removePaymentAllocation,
  type AllocateToInvoicePayload,
  type PaymentCreate,
  type PaymentListParams,
} from "@/api/payments";
import { invoicesKeys } from "@/hooks/useInvoices";
import { reconciliationKeys } from "@/hooks/useReconciliation";

export const paymentsKeys = {
  all: ["payments"] as const,
  lists: () => [...paymentsKeys.all, "list"] as const,
  list: (params?: PaymentListParams) => [...paymentsKeys.lists(), params ?? {}] as const,
  details: () => [...paymentsKeys.all, "detail"] as const,
  detail: (id: string) => [...paymentsKeys.details(), id] as const,
  receipt: (id: string) => [...paymentsKeys.all, "receipt", id] as const,
};

export function usePayments(params?: PaymentListParams) {
  return useQuery({
    queryKey: paymentsKeys.list(params),
    queryFn: () => listPayments(params),
  });
}

export function usePayment(id: string | undefined) {
  return useQuery({
    queryKey: paymentsKeys.detail(id ?? ""),
    queryFn: () => getPayment(id as string),
    enabled: !!id,
  });
}

export function useReceipt(paymentId: string | undefined) {
  return useQuery({
    queryKey: paymentsKeys.receipt(paymentId ?? ""),
    queryFn: () => getReceipt(paymentId as string),
    enabled: !!paymentId,
  });
}

export function useCreatePayment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PaymentCreate) => createPayment(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: paymentsKeys.all }),
  });
}

// Allocating/removing/reconciling all change Payment totals (which the
// Reconciliation dashboard is derived from) and the linked Invoice's
// amount_paid/balance/status (via PaymentAllocation.save()'s
// update_invoice_balance()) - keep all three namespaces in sync.
function invalidatePaymentRelatedCaches(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: paymentsKeys.all });
  queryClient.invalidateQueries({ queryKey: invoicesKeys.all });
  queryClient.invalidateQueries({ queryKey: reconciliationKeys.all });
}

export function useAllocateToInvoice(paymentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AllocateToInvoicePayload) => allocatePaymentToInvoice(paymentId, data),
    onSuccess: () => invalidatePaymentRelatedCaches(queryClient),
  });
}

export function useAllocateOldest(paymentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => allocatePaymentToOldest(paymentId),
    onSuccess: () => invalidatePaymentRelatedCaches(queryClient),
  });
}

export function useRemoveAllocation(paymentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (allocationId: string) => removePaymentAllocation(paymentId, allocationId),
    onSuccess: () => invalidatePaymentRelatedCaches(queryClient),
  });
}

export function useReconcilePayment(paymentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => reconcilePayment(paymentId),
    onSuccess: () => invalidatePaymentRelatedCaches(queryClient),
  });
}

// Not a server-state mutation in the usual sense (nothing to
// invalidate) - just wraps the blob fetch + triggers a real browser
// download via a throwaway anchor, since the endpoint requires the JWT
// Authorization header a plain <a href> navigation can't send.
export function useDownloadReceiptPdf() {
  return useMutation({
    mutationFn: async ({ paymentId, filename }: { paymentId: string; filename: string }) => {
      const blob = await downloadReceiptPdf(paymentId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    },
  });
}
