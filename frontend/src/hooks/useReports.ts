import { useQuery } from "@tanstack/react-query";
import {
  getCashFlowTrend,
  getLandlordSummary,
  getRentReport,
  getWaterReport,
  type CashFlowParams,
  type ReportDateRangeParams,
} from "@/api/reports";

export const reportsKeys = {
  all: ["reports"] as const,
  rent: (params?: ReportDateRangeParams) => [...reportsKeys.all, "rent", params ?? {}] as const,
  water: (params?: ReportDateRangeParams) => [...reportsKeys.all, "water", params ?? {}] as const,
  cashFlow: (params?: CashFlowParams) => [...reportsKeys.all, "cash-flow", params ?? {}] as const,
  landlordSummary: (params?: ReportDateRangeParams) =>
    [...reportsKeys.all, "landlord-summary", params ?? {}] as const,
};

export function useRentReport(params?: ReportDateRangeParams) {
  return useQuery({
    queryKey: reportsKeys.rent(params),
    queryFn: () => getRentReport(params),
  });
}

export function useWaterReport(params?: ReportDateRangeParams) {
  return useQuery({
    queryKey: reportsKeys.water(params),
    queryFn: () => getWaterReport(params),
  });
}

export function useCashFlowTrend(params?: CashFlowParams) {
  return useQuery({
    queryKey: reportsKeys.cashFlow(params),
    queryFn: () => getCashFlowTrend(params),
  });
}

export function useLandlordSummary(params?: ReportDateRangeParams) {
  return useQuery({
    queryKey: reportsKeys.landlordSummary(params),
    queryFn: () => getLandlordSummary(params),
  });
}
