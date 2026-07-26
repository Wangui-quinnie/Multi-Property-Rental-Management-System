import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { InvoiceTable } from "./InvoiceTable";
import type { Invoice } from "@/api/invoices";

const unpaidInvoice: Invoice = {
  id: "inv-1",
  lease: "lease-1",
  tenant_name: "John Kamau",
  unit_number: "A1",
  property_name: "Sunset Apartments",
  billing_period: "period-1",
  billing_period_name: "January 2026",
  invoice_number: "INV-202601-LEASE1",
  invoice_date: "2026-01-01",
  due_date: "2026-01-05",
  subtotal: "15000.00",
  tax_amount: "0.00",
  total_amount: "15000.00",
  amount_paid: "0.00",
  balance: "15000.00",
  status: "UNPAID",
  is_overdue: false,
  items: [],
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const overdueInvoice: Invoice = {
  ...unpaidInvoice,
  id: "inv-2",
  status: "UNPAID", // persisted status hasn't caught up yet (see is_currently_overdue())
  is_overdue: true,
};

describe("InvoiceTable", () => {
  it("renders a row with the invoice's details", () => {
    render(<InvoiceTable invoices={[unpaidInvoice]} isLoading={false} onViewDetail={vi.fn()} />);

    expect(screen.getByText("INV-202601-LEASE1")).toBeInTheDocument();
    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("Sunset Apartments - A1")).toBeInTheDocument();
  });

  it("shows OVERDUE when is_overdue is true, even if the persisted status hasn't caught up", () => {
    render(<InvoiceTable invoices={[overdueInvoice]} isLoading={false} onViewDetail={vi.fn()} />);
    expect(screen.getByText("OVERDUE")).toBeInTheDocument();
  });

  it("shows the persisted status when not overdue", () => {
    render(<InvoiceTable invoices={[unpaidInvoice]} isLoading={false} onViewDetail={vi.fn()} />);
    expect(screen.getByText("UNPAID")).toBeInTheDocument();
  });

  it("calls onViewDetail with the invoice when View is clicked", async () => {
    const onViewDetail = vi.fn();
    const user = userEvent.setup();
    render(<InvoiceTable invoices={[unpaidInvoice]} isLoading={false} onViewDetail={onViewDetail} />);

    await user.click(screen.getByRole("button", { name: /view/i }));
    expect(onViewDetail).toHaveBeenCalledWith(unpaidInvoice);
  });

  it("shows an empty-state message when there are no invoices", () => {
    render(<InvoiceTable invoices={[]} isLoading={false} onViewDetail={vi.fn()} />);
    expect(screen.getByText("No invoices yet.")).toBeInTheDocument();
  });
});
