import { apiClient } from "./client";
import type { components, operations } from "@/types/api";

/**
 * The `renew`/`terminate` @action endpoints return success_response()'s
 * {success, message, data} envelope at runtime (confirmed by reading
 * apps/leases/views/lease.py), but the generated schema types describe
 * the response as the bare Lease object AND misdescribe the request
 * body as the full Lease schema (it's actually LeaseRenewSerializer/
 * LeaseTerminateSerializer - drf-spectacular can't see the serializer
 * manually instantiated inside the action body). Same class of gap as
 * Property's restore/dashboard - see api/properties.ts's Envelope/unwrap.
 */
interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(promise: Promise<{ data: Envelope<T> }>): Promise<T> {
  return promise.then((res) => res.data.data);
}

export type Lease = components["schemas"]["Lease"];
export type LeaseCreate = components["schemas"]["LeaseCreate"];

/**
 * LeaseUpdateSerializer's `status` field technically accepts
 * ACTIVE/ENDED/CANCELLED, but a plain PATCH to ENDED skips
 * terminate_lease()'s atomic cleanup (ending the Occupancy, freeing
 * the Unit, opening a VacancyPeriod). This app deliberately only
 * exposes ACTIVE/CANCELLED here - ending a lease is only ever done
 * via terminateLease() below.
 */
export type LeaseUpdate = Omit<components["schemas"]["LeaseUpdate"], "status"> & {
  status?: "ACTIVE" | "CANCELLED";
};

// `status`/`unit`/`tenant` are real, working exact-match filters (added
// via filterset_fields) but aren't in the generated schema since they
// were added after the last sync-types run.
export type LeaseListParams = NonNullable<operations["leases_list"]["parameters"]["query"]> & {
  status?: "ACTIVE" | "ENDED" | "CANCELLED";
  unit?: string;
  tenant?: string;
};
export type PaginatedLeases = components["schemas"]["PaginatedLeaseList"];

export interface LeaseRenewPayload {
  new_lease_start_date: string;
  new_lease_end_date?: string | null;
  rent_amount: string;
  deposit_amount?: string;
  billing_day: number;
}

export interface LeaseTerminatePayload {
  termination_date?: string;
}

export function listLeases(params?: LeaseListParams) {
  return apiClient.get<PaginatedLeases>("/leases/", { params }).then((res) => res.data);
}

export function getLease(id: string) {
  return apiClient.get<Lease>(`/leases/${id}/`).then((res) => res.data);
}

export function createLease(data: LeaseCreate) {
  return apiClient.post<LeaseCreate>("/leases/", data).then((res) => res.data);
}

export function updateLease(id: string, data: LeaseUpdate) {
  return apiClient.put<LeaseUpdate>(`/leases/${id}/`, data).then((res) => res.data);
}

export function renewLease(id: string, data: LeaseRenewPayload) {
  return unwrap<Lease>(apiClient.post(`/leases/${id}/renew/`, data));
}

export function terminateLease(id: string, data: LeaseTerminatePayload) {
  return unwrap<Lease>(apiClient.post(`/leases/${id}/terminate/`, data));
}