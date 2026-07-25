import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  archiveProperty,
  createProperty,
  getProperty,
  getPropertyDashboard,
  listProperties,
  restoreProperty,
  updateProperty,
  type PropertyCreate,
  type PropertyListParams,
  type PropertyUpdate,
} from "@/api/properties";

export const propertiesKeys = {
  all: ["properties"] as const,
  lists: () => [...propertiesKeys.all, "list"] as const,
  list: (params?: PropertyListParams) => [...propertiesKeys.lists(), params ?? {}] as const,
  details: () => [...propertiesKeys.all, "detail"] as const,
  detail: (id: string) => [...propertiesKeys.details(), id] as const,
  dashboard: () => [...propertiesKeys.all, "dashboard"] as const,
};

export function useProperties(params?: PropertyListParams) {
  return useQuery({
    queryKey: propertiesKeys.list(params),
    queryFn: () => listProperties(params),
  });
}

export function useProperty(id: string | undefined) {
  return useQuery({
    queryKey: propertiesKeys.detail(id ?? ""),
    queryFn: () => getProperty(id as string),
    enabled: !!id,
  });
}

export function usePropertyDashboard() {
  return useQuery({
    queryKey: propertiesKeys.dashboard(),
    queryFn: getPropertyDashboard,
  });
}

export function useCreateProperty() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PropertyCreate) => createProperty(data),
    onSuccess: () => {
      // The create response has no `id` (see api/properties.ts), so
      // callers can't target a single detail cache entry — invalidate
      // the whole properties namespace (list + dashboard) instead.
      queryClient.invalidateQueries({ queryKey: propertiesKeys.all });
    },
  });
}

export function useUpdateProperty(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PropertyUpdate) => updateProperty(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: propertiesKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: propertiesKeys.lists() });
    },
  });
}

export function useArchiveProperty() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => archiveProperty(id),
    onSuccess: () => {
      // Archiving cascades to the property's units on the backend, so
      // invalidate units too, not just properties.
      queryClient.invalidateQueries({ queryKey: propertiesKeys.all });
      queryClient.invalidateQueries({ queryKey: ["units"] });
    },
  });
}

export function useRestoreProperty() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => restoreProperty(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: propertiesKeys.all });
      queryClient.invalidateQueries({ queryKey: ["units"] });
    },
  });
}