import { apiClient } from "./client";
import type { components, operations } from "@/types/api";

// ---- Tenants -----------------------------------------------------

export type Tenant = components["schemas"]["Tenant"];
export type TenantUpdate = components["schemas"]["TenantUpdate"];
export type TenantListParams = NonNullable<operations["tenants_list"]["parameters"]["query"]>;
export type PaginatedTenants = components["schemas"]["PaginatedTenantList"];

/**
 * The generated `TenantCreate` schema type is inaccurate as a request
 * payload type: drf-spectacular reuses one schema for both directions,
 * so it marks `id`/`created_at`/`updated_at` as required+readonly (we
 * don't have those yet when creating), and it doesn't reflect that
 * `email`, `username`, `first_name`, `last_name`, `phone_number`, and
 * `password` are all write_only=True on TenantCreateSerializer. This
 * is what we actually send.
 */
export interface TenantCreatePayload {
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  password: string;
  national_id?: string | null;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  status?: components["schemas"]["TenantStatusEnum"];
}

/**
 * ...and this is what actually comes back. Because email/username/
 * first_name/last_name/phone_number/password are write_only, NONE of
 * them appear in the response body - only the Tenant-profile fields.
 * Unlike Property/Unit's create response, `id` IS included here (it's
 * in TenantCreateSerializer.read_only_fields, not write_only), so
 * callers CAN use the returned id directly.
 */
export interface TenantCreateResponse {
  id: string;
  national_id: string | null;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  status: components["schemas"]["TenantStatusEnum"];
  created_at: string;
  updated_at: string;
}

export function listTenants(params?: TenantListParams) {
  return apiClient.get<PaginatedTenants>("/tenants/", { params }).then((res) => res.data);
}

export function getTenant(id: string) {
  return apiClient.get<Tenant>(`/tenants/${id}/`).then((res) => res.data);
}

export function createTenant(data: TenantCreatePayload) {
  return apiClient.post<TenantCreateResponse>("/tenants/", data).then((res) => res.data);
}

// PATCH (partial_update), matching the backend tests' usage - every
// field on TenantUpdateSerializer is optional (blank=True / has a
// default), so a partial update is the natural fit for a dialog that
// only ever edits national_id/emergency contact/status together.
export function updateTenant(id: string, data: TenantUpdate) {
  return apiClient.patch<TenantUpdate>(`/tenants/${id}/`, data).then((res) => res.data);
}