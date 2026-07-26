import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  activateOccupancy,
  getOccupancy,
  listOccupancies,
  type OccupancyActivatePayload,
  type OccupancyListParams,
} from "@/api/occupancy";
import { propertiesKeys } from "@/hooks/useProperties";
import { unitsKeys } from "@/hooks/useUnits";

export const occupancyKeys = {
  all: ["occupancy"] as const,
  lists: () => [...occupancyKeys.all, "list"] as const,
  list: (params?: OccupancyListParams) => [...occupancyKeys.lists(), params ?? {}] as const,
  details: () => [...occupancyKeys.all, "detail"] as const,
  detail: (id: string) => [...occupancyKeys.details(), id] as const,
};

export function useOccupancies(params?: OccupancyListParams) {
  return useQuery({
    queryKey: occupancyKeys.list(params),
    queryFn: () => listOccupancies(params),
  });
}

// Convenience wrapper for the common "does this lease already have an
// occupancy?" check (drives whether the Lease UI shows Activate vs
// Renew/Terminate) - relies on the ?lease= filter added to
// OccupancyViewSet this phase.
export function useOccupancyForLease(leaseId: string | undefined) {
  return useQuery({
    queryKey: occupancyKeys.list({ lease: leaseId ?? "" }),
    queryFn: () => listOccupancies({ lease: leaseId as string }),
    enabled: !!leaseId,
    select: (data) => data.results[0],
  });
}

export function useOccupancy(id: string | undefined) {
  return useQuery({
    queryKey: occupancyKeys.detail(id ?? ""),
    queryFn: () => getOccupancy(id as string),
    enabled: !!id,
  });
}

// Activating flips the Unit to OCCUPIED and closes any open
// VacancyPeriod (see activate_occupancy()), so those namespaces need
// invalidating alongside occupancy itself.
export function useActivateOccupancy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: OccupancyActivatePayload) => activateOccupancy(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: occupancyKeys.all });
      queryClient.invalidateQueries({ queryKey: ["vacancy"] });
      queryClient.invalidateQueries({ queryKey: unitsKeys.all });
      queryClient.invalidateQueries({ queryKey: propertiesKeys.all });
    },
  });
}