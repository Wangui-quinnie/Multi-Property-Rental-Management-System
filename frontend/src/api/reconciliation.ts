import { apiClient } from "./client";
import type { components } from "@/types/api";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

function unwrap<T>(promise: Promise<{ data: Envelope<T> }>): Promise<T> {
  return promise.then((res) => res.data.data);
}

// The generated schema claims GET /api/payments/reconciliation/ returns a
// bare ReconciliationDashboard, but the view wraps it via success_response
// like every other custom @action/APIView in this codebase - unwrap it
// the same way as Arrears/Vacancy dashboards.
export type ReconciliationDashboard = components["schemas"]["ReconciliationDashboard"];

export function getReconciliationDashboard() {
  return unwrap<ReconciliationDashboard>(apiClient.get("/payments/reconciliation/"));
}
