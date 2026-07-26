import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MyLeaseCard } from "./MyLeaseCard";
import { useOccupancyForLease } from "@/hooks/useOccupancy";
import type { Lease } from "@/api/leases";

vi.mock("@/hooks/useOccupancy");

const mockedUseOccupancyForLease = vi.mocked(useOccupancyForLease);

const sampleLease: Lease = {
  id: "lease-1",
  tenant: "tenant-1",
  tenant_name: "John Kamau",
  unit: "unit-1",
  unit_number: "A1",
  property_name: "Riverside Apartments",
  lease_start_date: "2026-01-01",
  lease_end_date: null,
  rent_amount: "25000.00",
  deposit_amount: "25000.00",
  billing_day: 5,
  status: "ACTIVE",
  created_at: "2026-01-01T10:00:00Z",
  updated_at: "2026-01-01T10:00:00Z",
};

describe("MyLeaseCard", () => {
  beforeEach(() => {
    mockedUseOccupancyForLease.mockReset();
  });

  it("renders the lease's details", () => {
    mockedUseOccupancyForLease.mockReturnValue({ data: undefined } as never);

    render(<MyLeaseCard lease={sampleLease} />);

    expect(screen.getByText("Riverside Apartments - A1")).toBeInTheDocument();
    expect(screen.getByText("ACTIVE")).toBeInTheDocument();
    // rent_amount and deposit_amount are both "25000.00" in this fixture.
    expect(screen.getAllByText("25000.00").length).toBe(2);
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("shows the move-in date when an occupancy record is found", () => {
    mockedUseOccupancyForLease.mockReturnValue({
      data: {
        id: "occ-1",
        lease: "lease-1",
        unit: "unit-1",
        tenant_name: "John Kamau",
        unit_number: "A1",
        property_name: "Riverside Apartments",
        move_in_date: "2026-01-02",
        move_out_date: null,
        status: "ACTIVE",
        created_at: "2026-01-02T10:00:00Z",
        updated_at: "2026-01-02T10:00:00Z",
      },
    } as never);

    render(<MyLeaseCard lease={sampleLease} />);

    expect(screen.getByText("Move-in date")).toBeInTheDocument();
    expect(screen.getByText("2026-01-02")).toBeInTheDocument();
  });

  it("omits the move-in date row when there is no occupancy record", () => {
    mockedUseOccupancyForLease.mockReturnValue({ data: undefined } as never);

    render(<MyLeaseCard lease={sampleLease} />);

    expect(screen.queryByText("Move-in date")).not.toBeInTheDocument();
  });
});
