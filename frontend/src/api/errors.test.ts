import { AxiosError, AxiosHeaders } from "axios";
import { describe, it, expect } from "vitest";
import { parseFieldErrors, getErrorMessage } from "./errors";

function makeAxiosError(data: unknown, status = 400) {
  return new AxiosError(
    "Request failed",
    "ERR_BAD_REQUEST",
    undefined,
    undefined,
    {
      status,
      statusText: "Bad Request",
      headers: {},
      config: { headers: new AxiosHeaders() },
      data,
    }
  );
}

describe("parseFieldErrors", () => {
  it("parses raw DRF validation error shape", () => {
    const error = makeAxiosError({
      code: ["Property with this code already exists."],
      landlord: ["Selected user must have the LANDLORD role."],
    });

    expect(parseFieldErrors(error)).toEqual({
      code: "Property with this code already exists.",
      landlord: "Selected user must have the LANDLORD role.",
    });
  });

  it("parses the enveloped {success, message, errors} shape", () => {
    const error = makeAxiosError({
      success: false,
      message: "Request failed",
      errors: { unit_number: ["A unit with this number already exists in this property."] },
    });

    expect(parseFieldErrors(error)).toEqual({
      unit_number: "A unit with this number already exists in this property.",
    });
  });

  it("returns an empty object for non-Axios errors", () => {
    expect(parseFieldErrors(new Error("boom"))).toEqual({});
    expect(parseFieldErrors(null)).toEqual({});
    expect(parseFieldErrors(undefined)).toEqual({});
  });

  it("returns an empty object when there is no response body", () => {
    const error = new AxiosError("Network Error");
    expect(parseFieldErrors(error)).toEqual({});
  });
});

describe("getErrorMessage", () => {
  it("prefers a top-level `message` field", () => {
    const error = makeAxiosError({ success: false, message: "Request failed." });
    expect(getErrorMessage(error)).toBe("Request failed.");
  });

  it("falls back to `detail`", () => {
    const error = makeAxiosError({ detail: "Authentication credentials were not provided." });
    expect(getErrorMessage(error)).toBe("Authentication credentials were not provided.");
  });

  it("falls back to the first field error", () => {
    const error = makeAxiosError({ name: ["This field is required."] });
    expect(getErrorMessage(error)).toBe("This field is required.");
  });

  it("falls back to the default message for non-Axios errors", () => {
    expect(getErrorMessage(new Error("boom"))).toBe("Something went wrong. Please try again.");
  });

  it("accepts a custom fallback", () => {
    expect(getErrorMessage(null, "")).toBe("");
  });
});