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

export type VacancyPeriod = components["schemas"]["VacancyPeriod"];
export type VacancyListParams = NonNullable<operations["vacancy_list"]["parameters"]["query"]>;
export type PaginatedVacancyPeriods = components["schemas"]["PaginatedVacancyPeriodList"];

// Real shape of GET /api/vacancy/dashboard/'s enveloped `data` field
// (get_vacancy_dashboard_for_user in apps/vacancy/selectors/vacancy.py).
// The generated schema wrongly claims this returns a bare VacancyPeriod.
export interface VacancyDashboard {
  currently_vacant_units: number;
  average_vacancy_duration_days: number;
  vacant_units: {
    unit_id: string;
    unit_number: string;
    vacated_at: string;
    days_vacant: number;
  }[];
}

// Read-only end to end - VacancyPeriod records are only ever
// created/closed internally by Lease Termination and Occupancy
// Activation, never directly through this API.
export function listVacancyPeriods(params?: VacancyListParams) {
  return apiClient.get<PaginatedVacancyPeriods>("/vacancy/", { params }).then((res) => res.data);
}

export function getVacancyDashboard() {
  return unwrap<VacancyDashboard>(apiClient.get("/vacancy/dashboard/"));
}