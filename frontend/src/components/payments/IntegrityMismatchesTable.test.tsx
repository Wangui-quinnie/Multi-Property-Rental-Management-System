import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { IntegrityMismatchesTable } from "./IntegrityMismatchesTable";

describe("IntegrityMismatchesTable", () => {
  it("renders an over-allocated payment mismatch", () => {
    render(
      <IntegrityMismatchesTable
        isLoading={false}
        entries={[
          {
            type: "OVER_ALLOCATED_PAYMENT",
            payment_id: "payment-1",
            payment_reference: "PAY-000001",
            amount: "5000.00",
            total_allocated: "6000.00",
            difference: "1000.00",
          },
        ]}
      />
    );

    expect(screen.getByText("OVER_ALLOCATED_PAYMENT")).toBeInTheDocument();
    expect(screen.getByText("PAY-000001")).toBeInTheDocument();
    expect(screen.getByText(/over by 1000.00/)).toBeInTheDocument();
  });

  it("renders an invoice amount_paid mismatch", () => {
    render(
      <IntegrityMismatchesTable
        isLoading={false}
        entries={[
          {
            type: "INVOICE_AMOUNT_PAID_MISMATCH",
            invoice_id: "inv-1",
            invoice_number: "INV-1",
            recorded_amount_paid: "5000.00",
            actual_allocated_total: "4000.00",
          },
        ]}
      />
    );

    expect(screen.getByText("INVOICE_AMOUNT_PAID_MISMATCH")).toBeInTheDocument();
    expect(screen.getByText("INV-1")).toBeInTheDocument();
    expect(screen.getByText(/Recorded 5000.00, actual 4000.00/)).toBeInTheDocument();
  });

  it("shows an empty-state message when there are none", () => {
    render(<IntegrityMismatchesTable isLoading={false} entries={[]} />);
    expect(
      screen.getByText("No integrity mismatches - everything reconciles cleanly.")
    ).toBeInTheDocument();
  });
});
