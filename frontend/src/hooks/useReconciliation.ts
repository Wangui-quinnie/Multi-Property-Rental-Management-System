import { useQuery } from "@tanstack/react-query";
import { getReconciliationDashboard } from "@/api/reconciliation";

export const reconciliationKeys = {
  all: ["reconciliation"] as const,
  dashboard: () => [...reconciliationKeys.all, "dashboard"] as const,
};

export function useReconciliationDashboard() {
  return useQuery({
    queryKey: reconciliationKeys.dashboard(),
    queryFn: getReconciliationDashboard,
  });
}
