import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  applyLateFee,
  applyLateFeesBatch,
  generateRentInvoices,
  getArrearsDashboard,
  getInvoice,
  listInvoices,
  markOverdueInvoices,
  type ApplyLateFeePayload,
  type ApplyLateFeesBatchPayload,
  type GenerateRentInvoicesPayload,
  type InvoiceListParams,
} from "@/api/invoices";

export const invoicesKeys = {
  all: ["invoices"] as const,
  lists: () => [...invoicesKeys.all, "list"] as const,
  list: (params?: InvoiceListParams) => [...invoicesKeys.lists(), params ?? {}] as const,
  details: () => [...invoicesKeys.all, "detail"] as const,
  detail: (id: string) => [...invoicesKeys.details(), id] as const,
  arrears: () => [...invoicesKeys.all, "arrears"] as const,
};

export function useInvoices(params?: InvoiceListParams) {
  return useQuery({
    queryKey: invoicesKeys.list(params),
    queryFn: () => listInvoices(params),
  });
}

export function useInvoice(id: string | undefined) {
  return useQuery({
    queryKey: invoicesKeys.detail(id ?? ""),
    queryFn: () => getInvoice(id as string),
    enabled: !!id,
  });
}

export function useArrearsDashboard() {
  return useQuery({
    queryKey: invoicesKeys.arrears(),
    queryFn: getArrearsDashboard,
  });
}

// Every mutation below changes Invoice totals/status, which the Arrears
// dashboard is derived from - always invalidate both namespaces together
// so a stale arrears view can't linger after generating/fee-ing/marking.
function invalidateInvoiceAndArrearsCaches(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: invoicesKeys.all });
}

export function useGenerateRentInvoices() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GenerateRentInvoicesPayload) => generateRentInvoices(data),
    onSuccess: () => invalidateInvoiceAndArrearsCaches(queryClient),
  });
}

export function useApplyLateFee(invoiceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ApplyLateFeePayload) => applyLateFee(invoiceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: invoicesKeys.detail(invoiceId) });
      invalidateInvoiceAndArrearsCaches(queryClient);
    },
  });
}

export function useApplyLateFeesBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ApplyLateFeesBatchPayload) => applyLateFeesBatch(data),
    onSuccess: () => invalidateInvoiceAndArrearsCaches(queryClient),
  });
}

export function useMarkOverdueInvoices() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => markOverdueInvoices(),
    onSuccess: () => invalidateInvoiceAndArrearsCaches(queryClient),
  });
}
