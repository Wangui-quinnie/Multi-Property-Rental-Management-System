import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createTenant,
  getTenant,
  listTenants,
  updateTenant,
  type TenantCreatePayload,
  type TenantListParams,
  type TenantUpdate,
} from "@/api/tenants";

export const tenantsKeys = {
  all: ["tenants"] as const,
  lists: () => [...tenantsKeys.all, "list"] as const,
  list: (params?: TenantListParams) => [...tenantsKeys.lists(), params ?? {}] as const,
  details: () => [...tenantsKeys.all, "detail"] as const,
  detail: (id: string) => [...tenantsKeys.details(), id] as const,
};

export function useTenants(params?: TenantListParams) {
  return useQuery({
    queryKey: tenantsKeys.list(params),
    queryFn: () => listTenants(params),
  });
}

export function useTenant(id: string | undefined) {
  return useQuery({
    queryKey: tenantsKeys.detail(id ?? ""),
    queryFn: () => getTenant(id as string),
    enabled: !!id,
  });
}

export function useCreateTenant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TenantCreatePayload) => createTenant(data),
    onSuccess: () => {
      // Create response has no email/name (write_only, see api/tenants.ts),
      // so there's nothing worth patching into an existing cache entry -
      // just invalidate the whole tenants namespace.
      queryClient.invalidateQueries({ queryKey: tenantsKeys.all });
    },
  });
}

export function useUpdateTenant(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TenantUpdate) => updateTenant(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tenantsKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: tenantsKeys.lists() });
    },
  });
}