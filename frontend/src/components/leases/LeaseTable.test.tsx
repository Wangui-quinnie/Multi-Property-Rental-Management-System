import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi } from "vitest";
import { LeaseTable } from "./LeaseTable";
import type { Lease } from "@/api/leases";

const activeLease: Lease = {
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

const endedLease: Lease = { ...activeLease, id: "lease-2", status: "ENDED" };

function renderTable(leases: Lease[], onManage = vi.fn()) {
  return render(
    <MemoryRouter>
      <LeaseTable leases={leases} isLoading={false} onManage={onManage} />
    </MemoryRouter>
  );
}

describe("LeaseTable", () => {
  it("renders a row with the lease's details", () => {
    renderTable([activeLease]);
    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("Sunset Apartments - A1")).toBeInTheDocument();
    expect(screen.getByText("ACTIVE")).toBeInTheDocument();
  });

  it("shows Edit/Manage actions only for ACTIVE leases", () => {
    renderTable([activeLease, endedLease]);

    // The "Edit" element is a Base UI Button polymorphically rendered as an
    // anchor (render={<Link .../>} nativeButton={false}), which explicitly
    // sets role="button" on the <a> - so it has no implicit "link" role and
    // must be queried via role "button", not "link".
    expect(screen.getAllByRole("button", { name: /manage/i })).toHaveLength(1);
    expect(screen.getAllByRole("button", { name: /^edit/i })).toHaveLength(1);
  });

  it("shows an empty-state message when there are no leases", () => {
    renderTable([]);
    expect(screen.getByText("No leases yet.")).toBeInTheDocument();
  });

  it("calls onManage with the lease when Manage is clicked", async () => {
    const onManage = vi.fn();
    const user = userEvent.setup();
    renderTable([activeLease], onManage);

    await user.click(screen.getByRole("button", { name: /manage/i }));
    expect(onManage).toHaveBeenCalledWith(activeLease);
  });
});