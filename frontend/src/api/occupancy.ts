import { apiClient } from "./client";
import type { components, operations } from "@/types/api";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(promise: Promise<{ data: Envelope<T> }>): Promise<T> {
  return promise.then((res) => res.data.data);
}

export type Occupancy = components["schemas"]["Occupancy"];

// `lease`/`unit`/`status` are real, working exact-match filters (added
// via filterset_fields) but aren't in the generated schema since they
// were added after the last sync-types run.
export type OccupancyListParams = NonNullable<operations["occupancy_list"]["parameters"]["query"]> & {
  lease?: string;
  unit?: string;
  status?: "ACTIVE" | "ENDED";
};
export type PaginatedOccupancies = components["schemas"]["PaginatedOccupancyList"];

export interface OccupancyActivatePayload {
  lease: string;
  move_in_date?: string;
}

export function listOccupancies(params?: OccupancyListParams) {
  return apiClient.get<PaginatedOccupancies>("/occupancy/", { params }).then((res) => res.data);
}

export function getOccupancy(id: string) {
  return apiClient.get<Occupancy>(`/occupancy/${id}/`).then((res) => res.data);
}

// Restricted to Admin/Landlord server-side (activate_occupancy() raises
// PermissionDenied for anyone else) - callers should still gate the UI
// action to those roles rather than relying solely on the 403.
export function activateOccupancy(data: OccupancyActivatePayload) {
  return unwrap<Occupancy>(apiClient.post("/occupancy/activate/", data));
}