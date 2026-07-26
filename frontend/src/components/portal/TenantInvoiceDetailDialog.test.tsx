import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { TenantInvoiceDetailDialog } from "./TenantInvoiceDetailDialog";
import type { Invoice } from "@/api/invoices";

const sampleInvoice: Invoice = {
  id: "inv-1",
  lease: "lease-1",
  tenant_name: "John Kamau",
  unit_number: "A1",
  property_name: "Riverside Apartments",
  billing_period: "period-1",
  billing_period_name: "January 2026",
  invoice_number: "INV-000001",
  invoice_date: "2026-01-01",
  due_date: "2026-01-10",
  subtotal: "25000.00",
  tax_amount: "0.00",
  total_amount: "25000.00",
  amount_paid: "0.00",
  balance: "25000.00",
  status: "OVERDUE",
  is_overdue: true,
  items: [
    {
      id: "item-1",
      item_type: "RENT",
      description: "January rent",
      quantity: "1.00",
      unit_price: "25000.00",
      amount: "25000.00",
      created_at: "2026-01-01T10:00:00Z",
    },
  ],
  created_at: "2026-01-01T10:00:00Z",
  updated_at: "2026-01-01T10:00:00Z",
};

describe("TenantInvoiceDetailDialog", () => {
  it("renders invoice details and line items without an apply-late-fee form", () => {
    render(
      <TenantInvoiceDetailDialog open onOpenChange={vi.fn()} invoice={sampleInvoice} />
    );

    expect(screen.getByText("Invoice INV-000001")).toBeInTheDocument();
    expect(screen.getByText("Riverside Apartments - A1")).toBeInTheDocument();
    expect(screen.getByText("OVERDUE")).toBeInTheDocument();
    expect(screen.getByText("January rent")).toBeInTheDocument();

    // Read-only for a Tenant - no late-fee action should ever render here.
    expect(screen.queryByText(/apply late fee/i)).not.toBeInTheDocument();
  });
});
