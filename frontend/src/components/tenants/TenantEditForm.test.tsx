import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError, AxiosHeaders } from "axios";
import { describe, it, expect, vi } from "vitest";
import { TenantEditForm } from "./TenantEditForm";
import type { Tenant } from "@/api/tenants";

function makeAxiosError(data: unknown) {
  return new AxiosError("Request failed", "ERR_BAD_REQUEST", undefined, undefined, {
    status: 400,
    statusText: "Bad Request",
    headers: {},
    config: { headers: new AxiosHeaders() },
    data,
  });
}

const sampleTenant: Tenant = {
  id: "tenant-1",
  email: "john@example.com",
  full_name: "John Kamau",
  phone_number: "0700000000",
  national_id: "12345678",
  emergency_contact_name: "Jane Doe",
  emergency_contact_phone: "0711111111",
  status: "ACTIVE",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("TenantEditForm", () => {
  it("pre-fills from the tenant prop", () => {
    render(
      <TenantEditForm tenant={sampleTenant} onSubmit={vi.fn()} isSubmitting={false} submitError={null} />
    );

    expect(screen.getByLabelText("National ID")).toHaveValue("12345678");
    expect(screen.getByLabelText("Emergency contact name")).toHaveValue("Jane Doe");
    expect(screen.getByLabelText("Emergency contact phone")).toHaveValue("0711111111");
    expect(screen.getByLabelText("Status")).toHaveValue("ACTIVE");
  });

  it("does not render any User fields (email/name/phone/password)", () => {
    render(
      <TenantEditForm tenant={sampleTenant} onSubmit={vi.fn()} isSubmitting={false} submitError={null} />
    );

    expect(screen.queryByLabelText(/^email/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/^password/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText("First name")).not.toBeInTheDocument();
  });

  it("submits national_id/emergency contact/status, including a status change", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(
      <TenantEditForm tenant={sampleTenant} onSubmit={onSubmit} isSubmitting={false} submitError={null} />
    );

    await user.selectOptions(screen.getByLabelText("Status"), "BLACKLISTED");
    await user.click(screen.getByRole("button", { name: /save changes/i }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        national_id: "12345678",
        emergency_contact_name: "Jane Doe",
        emergency_contact_phone: "0711111111",
        status: "BLACKLISTED",
      })
    );
  });

  it("shows field-level errors from the backend", () => {
    render(
      <TenantEditForm
        tenant={sampleTenant}
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={makeAxiosError({ status: ["Not a valid status choice."] })}
      />
    );

    expect(screen.getByText("Not a valid status choice.")).toBeInTheDocument();
  });
});