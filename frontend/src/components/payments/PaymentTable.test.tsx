import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { PaymentTable } from "./PaymentTable";
import type { Payment } from "@/api/payments";

// unallocated_amount is deliberately different from amount here (even
// though total_allocated is 0) purely so the Amount/Unallocated columns
// don't collide on the same text in getByText assertions below - this
// component only displays whatever it's given, it doesn't compute
// unallocated_amount itself.
const samplePayment: Payment = {
  id: "payment-1",
  tenant: "tenant-1",
  tenant_name: "John Kamau",
  payment_reference: "PAY-000001",
  payment_method: "CASH",
  amount: "15000.00",
  payment_date: "2026-01-05T10:00:00Z",
  status: "CONFIRMED",
  notes: "",
  is_reconciled: false,
  reconciled_at: null,
  reconciled_by_name: null,
  allocations: [],
  total_allocated: "0.00",
  unallocated_amount: "10000.00",
  created_at: "2026-01-05T10:00:00Z",
  updated_at: "2026-01-05T10:00:00Z",
};

describe("PaymentTable", () => {
  it("renders a row with the payment's details", () => {
    render(<PaymentTable payments={[samplePayment]} isLoading={false} onManage={vi.fn()} />);

    expect(screen.getByText("PAY-000001")).toBeInTheDocument();
    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("15000.00")).toBeInTheDocument();
    expect(screen.getByText("No")).toBeInTheDocument();
  });

  it("calls onManage with the payment when Manage is clicked", async () => {
    const onManage = vi.fn();
    const user = userEvent.setup();
    render(<PaymentTable payments={[samplePayment]} isLoading={false} onManage={onManage} />);

    await user.click(screen.getByRole("button", { name: /manage/i }));
    expect(onManage).toHaveBeenCalledWith(samplePayment);
  });

  it("shows an empty-state message when there are no payments", () => {
    render(<PaymentTable payments={[]} isLoading={false} onManage={vi.fn()} />);
    expect(screen.getByText("No payments yet.")).toBeInTheDocument();
  });
});
