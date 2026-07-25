import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  archiveUnit,
  createUnit,
  getUnit,
  getUnitDashboard,
  listUnits,
  restoreUnit,
  updateUnit,
  type UnitCreate,
  type UnitListParams,
  type UnitUpdate,
} from "@/api/properties";
import { propertiesKeys } from "@/hooks/useProperties";

export const unitsKeys = {
  all: ["units"] as const,
  lists: () => [...unitsKeys.all, "list"] as const,
  list: (params?: UnitListParams) => [...unitsKeys.lists(), params ?? {}] as const,
  details: () => [...unitsKeys.all, "detail"] as const,
  detail: (id: string) => [...unitsKeys.details(), id] as const,
  dashboard: () => [...unitsKeys.all, "dashboard"] as const,
};

export function useUnits(params?: UnitListParams) {
  return useQuery({
    queryKey: unitsKeys.list(params),
    queryFn: () => listUnits(params),
  });
}

export function useUnit(id: string | undefined) {
  return useQuery({
    queryKey: unitsKeys.detail(id ?? ""),
    queryFn: () => getUnit(id as string),
    enabled: !!id,
  });
}

export function useUnitDashboard() {
  return useQuery({
    queryKey: unitsKeys.dashboard(),
    queryFn: getUnitDashboard,
  });
}

// A Unit's parent Property carries rolled-up stats (total_units,
// occupied_units, occupancy_rate, potential_monthly_rent), so any
// mutation that changes a unit's existence or status must also
// invalidate the properties namespace to keep those numbers honest.
function invalidateUnitAndPropertyCaches(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: unitsKeys.all });
  queryClient.invalidateQueries({ queryKey: propertiesKeys.all });
}

export function useCreateUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UnitCreate) => createUnit(data),
    onSuccess: () => invalidateUnitAndPropertyCaches(queryClient),
  });
}

export function useUpdateUnit(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UnitUpdate) => updateUnit(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: unitsKeys.detail(id) });
      invalidateUnitAndPropertyCaches(queryClient);
    },
  });
}

export function useArchiveUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => archiveUnit(id),
    onSuccess: () => invalidateUnitAndPropertyCaches(queryClient),
  });
}

export function useRestoreUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => restoreUnit(id),
    onSuccess: () => invalidateUnitAndPropertyCaches(queryClient),
  });
}