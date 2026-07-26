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

export type WaterMeterReading = components["schemas"]["WaterMeterReading"];
export type WaterMeterReadingCreate = components["schemas"]["WaterMeterReadingCreate"];
export type WaterMeterReadingUpdate = components["schemas"]["WaterMeterReadingUpdate"];

export type WaterReadingListParams = NonNullable<
  operations["billing_water_readings_list"]["parameters"]["query"]
> & {
  billing_period?: string;
  unit?: string;
};
export type PaginatedWaterReadings = components["schemas"]["PaginatedWaterMeterReadingList"];

export function listWaterReadings(params?: WaterReadingListParams) {
  return apiClient
    .get<PaginatedWaterReadings>("/billing/water-readings/", { params })
    .then((res) => res.data);
}

export function getWaterReading(id: string) {
  return apiClient.get<WaterMeterReading>(`/billing/water-readings/${id}/`).then((res) => res.data);
}

export function createWaterReading(data: WaterMeterReadingCreate) {
  return apiClient
    .post<WaterMeterReading>("/billing/water-readings/", data)
    .then((res) => res.data);
}

export function updateWaterReading(id: string, data: WaterMeterReadingUpdate) {
  return apiClient
    .put<WaterMeterReading>(`/billing/water-readings/${id}/`, data)
    .then((res) => res.data);
}

// Backend rejects (400) deleting a reading that's already been billed
// (has an invoice_item) - surfaced via getErrorMessage, not special-cased
// here.
export function deleteWaterReading(id: string) {
  return apiClient.delete<void>(`/billing/water-readings/${id}/`).then(() => undefined);
}

export function applyWaterCharge(id: string) {
  return unwrap<WaterMeterReading>(apiClient.post(`/billing/water-readings/${id}/apply-charge/`));
}
