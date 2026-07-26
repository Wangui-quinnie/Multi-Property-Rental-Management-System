import { useQuery } from "@tanstack/react-query";
import { getVacancyDashboard, listVacancyPeriods, type VacancyListParams } from "@/api/vacancy";

export const vacancyKeys = {
  all: ["vacancy"] as const,
  lists: () => [...vacancyKeys.all, "list"] as const,
  list: (params?: VacancyListParams) => [...vacancyKeys.lists(), params ?? {}] as const,
  dashboard: () => [...vacancyKeys.all, "dashboard"] as const,
};

// Read-only namespace - VacancyPeriod records are only ever
// created/closed internally by Lease Termination and Occupancy
// Activation (see useLeases.ts/useOccupancy.ts, which both invalidate
// ["vacancy"] on those mutations).
export function useVacancyPeriods(params?: VacancyListParams) {
  return useQuery({
    queryKey: vacancyKeys.list(params),
    queryFn: () => listVacancyPeriods(params),
  });
}

export function useVacancyDashboard() {
  return useQuery({
    queryKey: vacancyKeys.dashboard(),
    queryFn: getVacancyDashboard,
  });
}