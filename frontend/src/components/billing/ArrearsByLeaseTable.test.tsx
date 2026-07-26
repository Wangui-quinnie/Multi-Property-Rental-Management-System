import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ArrearsByLeaseTable } from "./ArrearsByLeaseTable";

describe("ArrearsByLeaseTable", () => {
  it("renders a row per lease in arrears", () => {
    render(
      <ArrearsByLeaseTable
        isLoading={false}
        entries={[
          {
            lease_id: "lease-1",
            tenant_name: "John Kamau",
            unit_number: "A1",
            property_name: "Sunset Apartments",
            total_arrears: "15000.00",
            oldest_due_date: "2026-01-05",
            overdue_invoice_count: 2,
            days_in_arrears: 20,
          },
        ]}
      />
    );

    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("Sunset Apartments - A1")).toBeInTheDocument();
    expect(screen.getByText("15000.00")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();
  });

  it("shows an empty-state message when no leases are in arrears", () => {
    render(<ArrearsByLeaseTable isLoading={false} entries={[]} />);
    expect(screen.getByText("No leases in arrears.")).toBeInTheDocument();
  });
});
