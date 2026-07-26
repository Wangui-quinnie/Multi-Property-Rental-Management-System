import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createBillingPeriod,
  deleteBillingPeriod,
  getBillingPeriod,
  listBillingPeriods,
  updateBillingPeriod,
  type BillingPeriodListParams,
  type BillingPeriodWrite,
} from "@/api/billingPeriods";

export const billingPeriodsKeys = {
  all: ["billing-periods"] as const,
  lists: () => [...billingPeriodsKeys.all, "list"] as const,
  list: (params?: BillingPeriodListParams) => [...billingPeriodsKeys.lists(), params ?? {}] as const,
  details: () => [...billingPeriodsKeys.all, "detail"] as const,
  detail: (id: string) => [...billingPeriodsKeys.details(), id] as const,
};

export function useBillingPeriods(params?: BillingPeriodListParams) {
  return useQuery({
    queryKey: billingPeriodsKeys.list(params),
    queryFn: () => listBillingPeriods(params),
  });
}

export function useBillingPeriod(id: string | undefined) {
  return useQuery({
    queryKey: billingPeriodsKeys.detail(id ?? ""),
    queryFn: () => getBillingPeriod(id as string),
    enabled: !!id,
  });
}

export function useCreateBillingPeriod() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BillingPeriodWrite) => createBillingPeriod(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: billingPeriodsKeys.all }),
  });
}

export function useUpdateBillingPeriod(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BillingPeriodWrite) => updateBillingPeriod(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: billingPeriodsKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: billingPeriodsKeys.lists() });
    },
  });
}

export function useDeleteBillingPeriod() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteBillingPeriod(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: billingPeriodsKeys.all }),
  });
}
