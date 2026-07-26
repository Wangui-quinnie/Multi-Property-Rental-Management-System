import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError, AxiosHeaders } from "axios";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LeaseForm } from "./LeaseForm";
import { useTenants } from "@/hooks/useTenants";
import { useUnits } from "@/hooks/useUnits";
import type { Lease } from "@/api/leases";

function makeAxiosError(data: unknown) {
  return new AxiosError("Request failed", "ERR_BAD_REQUEST", undefined, undefined, {
    status: 400,
    statusText: "Bad Request",
    headers: {},
    config: { headers: new AxiosHeaders() },
    data,
  });
}

vi.mock("@/hooks/useTenants");
vi.mock("@/hooks/useUnits");

const mockedUseTenants = vi.mocked(useTenants);
const mockedUseUnits = vi.mocked(useUnits);

const sampleLease: Lease = {
  id: "lease-1",
  tenant: "tenant-1",
  tenant_name: "John Kamau",
  unit: "unit-1",
  unit_number: "A1",
  property_name: "Sunset Apartments",
  lease_start_date: "2026-01-01",
  lease_end_date: null,
  rent_amount: "15000.00",
  deposit_amount: "15000.00",
  billing_day: 1,
  status: "ACTIVE",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("LeaseForm", () => {
  beforeEach(() => {
    mockedUseTenants.mockReturnValue({
      data: { results: [{ id: "tenant-1", full_name: "John Kamau", email: "john@example.com" }] },
    } as never);
    mockedUseUnits.mockReturnValue({
      data: {
        results: [{ id: "unit-1", unit_number: "A1", property_name: "Sunset Apartments" }],
      },
    } as never);
  });

  it("shows tenant/unit pickers when creating", () => {
    render(<LeaseForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);

    // Tenant/Unit are required, so their accessible label text is
    // actually "Tenant *"/"Unit *" (see FormField's required asterisk) -
    // match with a case-insensitive regex, same convention as elsewhere.
    expect(screen.getByLabelText(/^tenant/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^unit/i)).toBeInTheDocument();
    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.queryByLabelText("Status")).not.toBeInTheDocument();
  });

  it("hides tenant/unit pickers and shows only ACTIVE/CANCELLED status options when editing", () => {
    render(
      <LeaseForm lease={sampleLease} onSubmit={vi.fn()} isSubmitting={false} submitError={null} />
    );

    expect(screen.queryByLabelText(/^tenant/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/^unit/i)).not.toBeInTheDocument();

    const statusSelect = screen.getByLabelText("Status") as HTMLSelectElement;
    const optionValues = Array.from(statusSelect.options).map((o) => o.value);
    expect(optionValues).toEqual(["ACTIVE", "CANCELLED"]);
    expect(optionValues).not.toContain("ENDED");
  });

  it("submits the create shape with tenant/unit ids", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(<LeaseForm onSubmit={onSubmit} isSubmitting={false} submitError={null} />);

    await user.selectOptions(screen.getByLabelText(/^tenant/i), "tenant-1");
    await user.selectOptions(screen.getByLabelText(/^unit/i), "unit-1");
    await user.type(screen.getByLabelText(/^lease start date/i), "2026-02-01");
    await user.type(screen.getByLabelText(/^rent amount/i), "20000");
    await user.click(screen.getByRole("button", { name: /create lease/i }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ tenant: "tenant-1", unit: "unit-1", rent_amount: "20000" })
    );
  });

  it("submits the update shape without tenant/unit", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(
      <LeaseForm lease={sampleLease} onSubmit={onSubmit} isSubmitting={false} submitError={null} />
    );

    await user.click(screen.getByRole("button", { name: /save changes/i }));

    const submitted = onSubmit.mock.calls[0][0];
    expect(submitted).not.toHaveProperty("tenant");
    expect(submitted).not.toHaveProperty("unit");
    expect(submitted.status).toBe("ACTIVE");
  });

  it("shows field-level errors from the backend", () => {
    render(
      <LeaseForm
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={makeAxiosError({ unit: ["This unit already has an active lease."] })}
      />
    );

    expect(screen.getByText("This unit already has an active lease.")).toBeInTheDocument();
  });
});