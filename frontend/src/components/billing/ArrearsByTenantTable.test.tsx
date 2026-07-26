import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ArrearsByTenantTable } from "./ArrearsByTenantTable";

describe("ArrearsByTenantTable", () => {
  it("renders a row per tenant in arrears", () => {
    render(
      <ArrearsByTenantTable
        isLoading={false}
        entries={[
          {
            tenant_id: "tenant-1",
            tenant_name: "John Kamau",
            total_arrears: "15000.00",
            overdue_invoice_count: 2,
            lease_count: 1,
          },
        ]}
      />
    );

    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("15000.00")).toBeInTheDocument();
  });

  it("shows an empty-state message when no tenants are in arrears", () => {
    render(<ArrearsByTenantTable isLoading={false} entries={[]} />);
    expect(screen.getByText("No tenants in arrears.")).toBeInTheDocument();
  });
});
