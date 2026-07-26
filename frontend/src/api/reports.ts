import { apiClient } from "./client";
import type { components } from "@/types/api";
import type { PortfolioDashboard } from "@/api/properties";
import type { VacancyDashboard } from "@/api/vacancy";
import type { ArrearsDashboard } from "@/api/invoices";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(promise: Promise<{ data: Envelope<T> }>): Promise<T> {
  return promise.then((res) => res.data.data);
}

export type RentReport = components["schemas"]["RentReport"];
export type WaterReport = components["schemas"]["WaterReport"];
export type CashFlowEntry = components["schemas"]["CashFlowEntry"];

// None of these query params (start_date/end_date/months) are declared
// via drf-spectacular OpenApiParameter decorators server-side, so they're
// entirely absent from the generated schema - hand-typed here, same as
// every other enveloped-action gap in this codebase.
export interface ReportDateRangeParams {
  start_date?: string;
  end_date?: string;
}

export interface CashFlowParams {
  months?: number;
}

// Real shape of the enveloped `data` field returned by GET
// /api/reports/landlord-summary/ (get_landlord_summary in
// apps/reports/selectors/reports.py). The generated schema claims this
// endpoint has no response body at all (`@extend_schema(responses=None)`
// server-side) - each section reuses the exact type of its own
// dedicated dashboard elsewhere in the API, since the selector composes
// the same underlying functions rather than re-deriving the numbers.
export interface LandlordSummary {
  occupancy: PortfolioDashboard;
  vacancy: VacancyDashboard;
  arrears: ArrearsDashboard;
  rent: RentReport;
  water: WaterReport;
  cash_flow: CashFlowEntry[];
}

export function getRentReport(params?: ReportDateRangeParams) {
  return unwrap<RentReport>(apiClient.get("/reports/rent/", { params }));
}

export function getWaterReport(params?: ReportDateRangeParams) {
  return unwrap<WaterReport>(apiClient.get("/reports/water/", { params }));
}

export function getCashFlowTrend(params?: CashFlowParams) {
  return unwrap<CashFlowEntry[]>(apiClient.get("/reports/cash-flow/", { params }));
}

export function getLandlordSummary(params?: ReportDateRangeParams) {
  return unwrap<LandlordSummary>(apiClient.get("/reports/landlord-summary/", { params }));
}
