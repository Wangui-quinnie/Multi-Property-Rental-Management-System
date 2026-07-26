import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  applyWaterCharge,
  createWaterReading,
  deleteWaterReading,
  getWaterReading,
  listWaterReadings,
  updateWaterReading,
  type WaterMeterReadingCreate,
  type WaterMeterReadingUpdate,
  type WaterReadingListParams,
} from "@/api/waterReadings";
import { invoicesKeys } from "@/hooks/useInvoices";

export const waterReadingsKeys = {
  all: ["water-readings"] as const,
  lists: () => [...waterReadingsKeys.all, "list"] as const,
  list: (params?: WaterReadingListParams) => [...waterReadingsKeys.lists(), params ?? {}] as const,
  details: () => [...waterReadingsKeys.all, "detail"] as const,
  detail: (id: string) => [...waterReadingsKeys.details(), id] as const,
};

export function useWaterReadings(params?: WaterReadingListParams) {
  return useQuery({
    queryKey: waterReadingsKeys.list(params),
    queryFn: () => listWaterReadings(params),
  });
}

export function useWaterReading(id: string | undefined) {
  return useQuery({
    queryKey: waterReadingsKeys.detail(id ?? ""),
    queryFn: () => getWaterReading(id as string),
    enabled: !!id,
  });
}

export function useCreateWaterReading() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WaterMeterReadingCreate) => createWaterReading(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: waterReadingsKeys.all }),
  });
}

export function useUpdateWaterReading(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WaterMeterReadingUpdate) => updateWaterReading(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: waterReadingsKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: waterReadingsKeys.lists() });
      // A correction to an already-billed reading resyncs its linked
      // InvoiceItem server-side (see apps/billing/services/water.py
      // update_water_reading) - invalidate Invoices too so the totals
      // shown in the Billing UI aren't stale.
      queryClient.invalidateQueries({ queryKey: invoicesKeys.all });
    },
  });
}

export function useDeleteWaterReading() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteWaterReading(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: waterReadingsKeys.all }),
  });
}

export function useApplyWaterCharge() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => applyWaterCharge(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: waterReadingsKeys.all });
      // Creates or adds a line item to an Invoice - keep the Invoices tab
      // and Arrears dashboard honest.
      queryClient.invalidateQueries({ queryKey: invoicesKeys.all });
    },
  });
}
