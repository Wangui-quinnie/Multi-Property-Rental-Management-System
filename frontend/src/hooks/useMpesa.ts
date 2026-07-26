import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getMpesaTransaction,
  initiateStkPush,
  listMpesaTransactions,
  type InitiateStkPushPayload,
  type MpesaTransactionListParams,
} from "@/api/mpesa";

export const mpesaKeys = {
  all: ["mpesa-transactions"] as const,
  lists: () => [...mpesaKeys.all, "list"] as const,
  list: (params?: MpesaTransactionListParams) => [...mpesaKeys.lists(), params ?? {}] as const,
  details: () => [...mpesaKeys.all, "detail"] as const,
  detail: (id: string) => [...mpesaKeys.details(), id] as const,
};

export function useMpesaTransactions(params?: MpesaTransactionListParams) {
  return useQuery({
    queryKey: mpesaKeys.list(params),
    queryFn: () => listMpesaTransactions(params),
  });
}

export function useMpesaTransaction(id: string | undefined) {
  return useQuery({
    queryKey: mpesaKeys.detail(id ?? ""),
    queryFn: () => getMpesaTransaction(id as string),
    enabled: !!id,
  });
}

export function useInitiateStkPush() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: InitiateStkPushPayload) => initiateStkPush(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: mpesaKeys.all }),
  });
}
