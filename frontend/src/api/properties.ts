import { apiClient } from "./client";
import type { components, operations } from "@/types/api";

/**
 * A handful of custom @action endpoints (restore, dashboard) — and the
 * new /api/auth/landlords/ list — return success_response()'s
 * {success, message, data} envelope at runtime, but the generated
 * OpenAPI types for them are inaccurate (drf-spectacular has no way to
 * know about the envelope unless explicitly told via an enveloped
 * response schema, which pre-existed as a gap for restore/dashboard
 * before this phase). Standard list/create/update/destroy are NOT
 * enveloped — those generated types are accurate as-is.
 *
 * This type + unwrap helper documents the real runtime shape for the
 * enveloped endpoints so we don't have to fight the generated types.
 */
interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(promise: Promise<{ data: Envelope<T> }>): Promise<T> {
  return promise.then((res) => res.data.data);
}

// ---- Properties ----------------------------------------------------

export type Property = components["schemas"]["Property"];
export type PropertyCreate = components["schemas"]["PropertyCreate"];
export type PropertyUpdate = components["schemas"]["PropertyUpdate"];
// `archived` is a real, working query param (read manually in
// get_queryset(), see apps/properties/views/property.py) but isn't
// documented in the OpenAPI schema since it's not a django-filter
// field — added by hand here rather than left as an `as never` cast
// at every call site.
export type PropertyListParams = NonNullable<operations["properties_list"]["parameters"]["query"]> & {
  archived?: "true" | "false";
};
export type PaginatedProperties = components["schemas"]["PaginatedPropertyList"];

// Shape of GET /api/properties/dashboard/ 's enveloped `data` field.
export interface PortfolioDashboard {
  total_properties: number;
  total_units: number;
  occupied_units: number;
  vacant_units: number;
  maintenance_units: number;
  occupancy_rate: number;
  potential_monthly_rent: number;
}

export function listProperties(params?: PropertyListParams) {
  return apiClient
    .get<PaginatedProperties>("/properties/", { params })
    .then((res) => res.data);
}

export function getProperty(id: string) {
  return apiClient.get<Property>(`/properties/${id}/`).then((res) => res.data);
}

export function createProperty(data: PropertyCreate) {
  // Real response body is PropertyCreateSerializer's own fields —
  // notably, it does NOT include `id`. Callers can't navigate straight
  // to a detail page after create; go back to the list instead.
  return apiClient.post<PropertyCreate>("/properties/", data).then((res) => res.data);
}

export function updateProperty(id: string, data: PropertyUpdate) {
  return apiClient.put<PropertyUpdate>(`/properties/${id}/`, data).then((res) => res.data);
}

export function archiveProperty(id: string) {
  // DELETE archives (soft-delete, cascades to units) rather than
  // hard-deleting. 204 No Content — nothing to return.
  return apiClient.delete<void>(`/properties/${id}/`).then(() => undefined);
}

export function restoreProperty(id: string) {
  return unwrap<Property>(apiClient.post(`/properties/${id}/restore/`));
}

export function getPropertyDashboard() {
  return unwrap<PortfolioDashboard>(apiClient.get("/properties/dashboard/"));
}

// ---- Units -----------------------------------------------------------

export type Unit = components["schemas"]["Unit"];
export type UnitCreate = components["schemas"]["UnitCreate"];
export type UnitUpdate = components["schemas"]["UnitUpdate"];
// See PropertyListParams above re: `archived` not being in the schema.
export type UnitListParams = NonNullable<operations["properties_units_list"]["parameters"]["query"]> & {
  archived?: "true" | "false";
};
export type PaginatedUnits = components["schemas"]["PaginatedUnitList"];

// Shape of GET /api/properties/units/dashboard/ 's enveloped `data` field.
export interface UnitDashboard {
  total_units: number;
  occupied_units: number;
  vacant_units: number;
  maintenance_units: number;
  inactive_units: number;
  occupancy_rate: number;
  average_rent: number;
  potential_monthly_rent: number;
}

export function listUnits(params?: UnitListParams) {
  return apiClient
    .get<PaginatedUnits>("/properties/units/", { params })
    .then((res) => res.data);
}

export function getUnit(id: string) {
  return apiClient.get<Unit>(`/properties/units/${id}/`).then((res) => res.data);
}

export function createUnit(data: UnitCreate) {
  // Same caveat as createProperty: response body is UnitCreateSerializer's
  // own fields, no `id` included.
  return apiClient.post<UnitCreate>("/properties/units/", data).then((res) => res.data);
}

export function updateUnit(id: string, data: UnitUpdate) {
  return apiClient.put<UnitUpdate>(`/properties/units/${id}/`, data).then((res) => res.data);
}

export function archiveUnit(id: string) {
  return apiClient.delete<void>(`/properties/units/${id}/`).then(() => undefined);
}

export function restoreUnit(id: string) {
  return unwrap<Unit>(apiClient.post(`/properties/units/${id}/restore/`));
}

export function getUnitDashboard() {
  return unwrap<UnitDashboard>(apiClient.get("/properties/units/dashboard/"));
}

// ---- Landlords (Admin-only reference list) ---------------------------

export type Landlord = components["schemas"]["LandlordList"];

export function listLandlords() {
  return unwrap<Landlord[]>(apiClient.get("/auth/landlords/"));
}