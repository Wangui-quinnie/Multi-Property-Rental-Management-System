import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MpesaTransactionTable } from "./MpesaTransactionTable";
import type { MpesaTransaction } from "@/api/mpesa";

const sampleTransaction: MpesaTransaction = {
  id: "txn-1",
  tenant: "tenant-1",
  tenant_name: "John Kamau",
  phone_number: "254712345678",
  amount: "5000.00",
  checkout_request_id: "ws_CO_123",
  mpesa_receipt_number: "",
  status: "PENDING",
  result_description: "",
  payment: null,
  created_at: "2026-01-05T10:00:00Z",
  updated_at: "2026-01-05T10:00:00Z",
};

describe("MpesaTransactionTable", () => {
  it("renders a row with the transaction's details", () => {
    render(<MpesaTransactionTable transactions={[sampleTransaction]} isLoading={false} />);

    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("254712345678")).toBeInTheDocument();
    expect(screen.getByText("ws_CO_123")).toBeInTheDocument();
    expect(screen.getByText("PENDING")).toBeInTheDocument();
  });

  it("shows a dash when there is no receipt number yet", () => {
    render(<MpesaTransactionTable transactions={[sampleTransaction]} isLoading={false} />);
    expect(screen.getByText("-")).toBeInTheDocument();
  });

  it("shows an empty-state message when there are no transactions", () => {
    render(<MpesaTransactionTable transactions={[]} isLoading={false} />);
    expect(screen.getByText("No M-Pesa transactions yet.")).toBeInTheDocument();
  });
});
