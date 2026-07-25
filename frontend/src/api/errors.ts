import { AxiosError } from "axios";

export type FieldErrors = Record<string, string>;

/**
 * Standard CRUD validation errors (create/update on ModelViewSets)
 * come back as raw DRF shape: { field: ["message", ...], non_field_errors: [...] }.
 * Custom @action / enveloped endpoints come back wrapped instead:
 * { success: false, message: "...", errors: { field: [...] } }.
 * (See api/properties.ts for why these two shapes coexist.)
 *
 * This normalizes either into a flat { field: "first message" } map
 * so form components never have to know which shape they're getting.
 */
export function parseFieldErrors(error: unknown): FieldErrors {
  if (!(error instanceof AxiosError) || !error.response) return {};

  const body = error.response.data;
  if (!body || typeof body !== "object") return {};

  const raw =
    "errors" in body && body.errors && typeof body.errors === "object"
      ? (body as { errors: Record<string, unknown> }).errors
      : (body as Record<string, unknown>);

  const result: FieldErrors = {};
  for (const [key, value] of Object.entries(raw)) {
    if (Array.isArray(value) && value.length > 0) {
      result[key] = String(value[0]);
    } else if (typeof value === "string") {
      result[key] = value;
    }
  }
  return result;
}

/** A single top-level message suitable for a general error banner. */
export function getErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again."
): string {
  if (error instanceof AxiosError && error.response?.data) {
    const body = error.response.data as Record<string, unknown>;
    if (typeof body.message === "string") return body.message;
    if (typeof body.detail === "string") return body.detail;
    const fieldErrors = parseFieldErrors(error);
    const firstFieldError = Object.values(fieldErrors)[0];
    if (firstFieldError) return firstFieldError;
  }
  return fallback;
}