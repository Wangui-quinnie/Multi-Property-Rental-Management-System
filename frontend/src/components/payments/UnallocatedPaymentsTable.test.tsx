import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { UnallocatedPaymentsTable } from "./UnallocatedPaymentsTable";

describe("UnallocatedPaymentsTable", () => {
  it("renders a row per unallocated payment", () => {
    render(
      <UnallocatedPaymentsTable
        isLoading={false}
        entries={[
          {
            payment_id: "payment-1",
            payment_reference: "PAY-000001",
            tenant_name: "John Kamau",
            amount: "15000.00",
            total_allocated: "5000.00",
            unallocated_amount: "10000.00",
          },
        ]}
      />
    );

    expect(screen.getByText("PAY-000001")).toBeInTheDocument();
    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("10000.00")).toBeInTheDocument();
  });

  it("shows an empty-state message when there are none", () => {
    render(<UnallocatedPaymentsTable isLoading={false} entries={[]} />);
    expect(screen.getByText("No unallocated payments.")).toBeInTheDocument();
  });
});
