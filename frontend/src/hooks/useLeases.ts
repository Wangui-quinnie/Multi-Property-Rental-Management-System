import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createLease,
  getLease,
  listLeases,
  renewLease,
  terminateLease,
  updateLease,
  type LeaseCreate,
  type LeaseListParams,
  type LeaseRenewPayload,
  type LeaseTerminatePayload,
  type LeaseUpdate,
} from "@/api/leases";
import { propertiesKeys } from "@/hooks/useProperties";
import { unitsKeys } from "@/hooks/useUnits";

export const leasesKeys = {
  all: ["leases"] as const,
  lists: () => [...leasesKeys.all, "list"] as const,
  list: (params?: LeaseListParams) => [...leasesKeys.lists(), params ?? {}] as const,
  details: () => [...leasesKeys.all, "detail"] as const,
  detail: (id: string) => [...leasesKeys.details(), id] as const,
};

export function useLeases(params?: LeaseListParams) {
  return useQuery({
    queryKey: leasesKeys.list(params),
    queryFn: () => listLeases(params),
  });
}

export function useLease(id: string | undefined) {
  return useQuery({
    queryKey: leasesKeys.detail(id ?? ""),
    queryFn: () => getLease(id as string),
    enabled: !!id,
  });
}

export function useCreateLease() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LeaseCreate) => createLease(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: leasesKeys.all });
    },
  });
}

export function useUpdateLease(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LeaseUpdate) => updateLease(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: leasesKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: leasesKeys.lists() });
    },
  });
}

// Renewal only ends the old lease + creates a new one - it never
// touches Occupancy/Unit/VacancyPeriod (see renew_lease() in
// apps/leases/services/lease.py), so only the leases namespace needs
// invalidating here.
export function useRenewLease(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LeaseRenewPayload) => renewLease(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: leasesKeys.all });
    },
  });
}

// Termination cascades broadly: ends the Occupancy, frees the Unit,
// and opens a VacancyPeriod (see terminate_lease()), all of which feed
// Property/Unit dashboard stats and the Vacancy dashboard - so this
// invalidates every namespace that could show stale data afterward.
export function useTerminateLease(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LeaseTerminatePayload) => terminateLease(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: leasesKeys.all });
      queryClient.invalidateQueries({ queryKey: ["occupancy"] });
      queryClient.invalidateQueries({ queryKey: ["vacancy"] });
      queryClient.invalidateQueries({ queryKey: unitsKeys.all });
      queryClient.invalidateQueries({ queryKey: propertiesKeys.all });
    },
  });
}