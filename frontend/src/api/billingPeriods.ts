import { apiClient } from "./client";
import type { components, operations } from "@/types/api";

export type BillingPeriod = components["schemas"]["BillingPeriod"];
export type BillingPeriodWrite = components["schemas"]["BillingPeriodWrite"];

export type BillingPeriodListParams = NonNullable<
  operations["billing_periods_list"]["parameters"]["query"]
> & {
  status?: "OPEN" | "CLOSED";
};
export type PaginatedBillingPeriods = components["schemas"]["PaginatedBillingPeriodList"];

export function listBillingPeriods(params?: BillingPeriodListParams) {
  return apiClient
    .get<PaginatedBillingPeriods>("/billing/periods/", { params })
    .then((res) => res.data);
}

export function getBillingPeriod(id: string) {
  return apiClient.get<BillingPeriod>(`/billing/periods/${id}/`).then((res) => res.data);
}

export function createBillingPeriod(data: BillingPeriodWrite) {
  return apiClient.post<BillingPeriod>("/billing/periods/", data).then((res) => res.data);
}

export function updateBillingPeriod(id: string, data: BillingPeriodWrite) {
  return apiClient.put<BillingPeriod>(`/billing/periods/${id}/`, data).then((res) => res.data);
}

// Admin-only in the backend (destroy() catches ProtectedError when
// WaterMeterReadings/Invoices still reference this period and returns a
// 400 with a clear message via error_response, instead of a raw 500).
export function deleteBillingPeriod(id: string) {
  return apiClient.delete<void>(`/billing/periods/${id}/`).then(() => undefined);
}
