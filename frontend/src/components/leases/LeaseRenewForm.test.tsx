import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LeaseRenewForm } from "./LeaseRenewForm";
import { useRenewLease } from "@/hooks/useLeases";
import type { Lease } from "@/api/leases";

vi.mock("@/hooks/useLeases");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseRenewLease = vi.mocked(useRenewLease);

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
  deposit_amount: "10000.00",
  billing_day: 5,
  status: "ACTIVE",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("LeaseRenewForm", () => {
  beforeEach(() => {
    mockedUseRenewLease.mockReset();
  });

  it("pre-fills rent/deposit/billing_day from the current lease", () => {
    mockedUseRenewLease.mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
      error: null,
    } as never);

    render(<LeaseRenewForm lease={sampleLease} onSuccess={vi.fn()} />);

    // Rent amount and Billing day are required, so their accessible label
    // text is actually "Rent amount *"/"Billing day *" (see FormField's
    // required asterisk) - match with a case-insensitive regex, same
    // convention as elsewhere (e.g. LeaseForm.test.tsx).
    expect(screen.getByLabelText(/^rent amount/i)).toHaveValue(15000);
    expect(screen.getByLabelText("Deposit amount")).toHaveValue(10000);
    expect(screen.getByLabelText(/^billing day/i)).toHaveValue(5);
  });

  it("submits the renewal payload", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseRenewLease.mockReturnValue({
      mutateAsync,
      isPending: false,
      error: null,
    } as never);

    const user = userEvent.setup();
    render(<LeaseRenewForm lease={sampleLease} onSuccess={vi.fn()} />);

    await user.type(screen.getByLabelText(/^new lease start date/i), "2027-01-01");
    await user.click(screen.getByRole("button", { name: /renew lease/i }));

    expect(mutateAsync).toHaveBeenCalledWith(
      expect.objectContaining({
        new_lease_start_date: "2027-01-01",
        rent_amount: "15000.00",
        deposit_amount: "10000.00",
        billing_day: 5,
      })
    );
  });
});