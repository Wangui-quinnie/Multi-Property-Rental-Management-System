import { useQuery } from "@tanstack/react-query";
import { listLandlords } from "@/api/properties";

// Admin-only reference list for the "create property for a landlord"
// picker. Landlords/Tenants get a 403 if this is ever called for them,
// so callers must gate the fetch itself via `enabled` (not just hide
// the UI), e.g. useLandlords({ enabled: isAdmin && !isEditMode }).
export function useLandlords(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["landlords"],
    queryFn: listLandlords,
    staleTime: 5 * 60 * 1000, // reference data, rarely changes mid-session
    enabled: options?.enabled ?? true,
  });
}