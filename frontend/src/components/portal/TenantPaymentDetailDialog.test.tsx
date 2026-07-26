import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { TenantPaymentDetailDialog } from "./TenantPaymentDetailDialog";
import { useReceipt, useDownloadReceiptPdf } from "@/hooks/usePayments";
import type { Payment } from "@/api/payments";

vi.mock("@/hooks/usePayments", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/hooks/usePayments")>();
  return { ...actual, useReceipt: vi.fn(), useDownloadReceiptPdf: vi.fn() };
});

const mockedUseReceipt = vi.mocked(useReceipt);
const mockedUseDownloadReceiptPdf = vi.mocked(useDownloadReceiptPdf);

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
  allocations: [
    { id: "alloc-1", invoice: "inv-1", invoice_number: "INV-000001", amount_allocated: "15000.00", created_at: "2026-01-05T10:00:00Z" } as never,
  ],
  total_allocated: "15000.00",
  unallocated_amount: "0.00",
  created_at: "2026-01-05T10:00:00Z",
  updated_at: "2026-01-05T10:00:00Z",
};

describe("TenantPaymentDetailDialog", () => {
  beforeEach(() => {
    mockedUseReceipt.mockReturnValue({ data: undefined, isLoading: false } as never);
    mockedUseDownloadReceiptPdf.mockReturnValue({ mutateAsync: vi.fn(), isPending: false } as never);
  });

  it("renders payment details and allocations without allocate/reconcile actions", () => {
    render(<TenantPaymentDetailDialog open onOpenChange={vi.fn()} payment={samplePayment} />);

    expect(screen.getByText("Payment PAY-000001")).toBeInTheDocument();
    expect(screen.getByText("INV-000001")).toBeInTheDocument();

    // Read-only for a Tenant - these Admin/Landlord-only actions must
    // never render here.
    expect(screen.queryByRole("button", { name: /allocate/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /remove/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /reconcile/i })).not.toBeInTheDocument();
  });

  it("opens the receipt dialog when View receipt is clicked", async () => {
    const user = userEvent.setup();
    render(<TenantPaymentDetailDialog open onOpenChange={vi.fn()} payment={samplePayment} />);

    await user.click(screen.getByRole("button", { name: /view receipt/i }));

    expect(mockedUseReceipt).toHaveBeenCalled();
  });
});
