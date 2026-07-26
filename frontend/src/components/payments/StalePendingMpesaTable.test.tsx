import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StalePendingMpesaTable } from "./StalePendingMpesaTable";

describe("StalePendingMpesaTable", () => {
  it("renders a row per stale transaction", () => {
    render(
      <StalePendingMpesaTable
        isLoading={false}
        entries={[
          {
            transaction_id: "txn-1",
            checkout_request_id: "ws_CO_123",
            tenant_name: "John Kamau",
            phone_number: "254712345678",
            amount: "5000.00",
            pending_since: "2026-01-05T10:00:00Z",
            hours_pending: 3.5,
          },
        ]}
      />
    );

    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("ws_CO_123")).toBeInTheDocument();
    expect(screen.getByText("3.5")).toBeInTheDocument();
  });

  it("shows an empty-state message when there are none", () => {
    render(<StalePendingMpesaTable isLoading={false} entries={[]} />);
    expect(screen.getByText("No stale pending M-Pesa transactions.")).toBeInTheDocument();
  });
});
