import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { AllocateToInvoiceForm } from "./AllocateToInvoiceForm";
import { useInvoices } from "@/hooks/useInvoices";
import { useAllocateToInvoice } from "@/hooks/usePayments";

vi.mock("@/hooks/useInvoices");
vi.mock("@/hooks/usePayments");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseInvoices = vi.mocked(useInvoices);
const mockedUseAllocateToInvoice = vi.mocked(useAllocateToInvoice);

describe("AllocateToInvoiceForm", () => {
  beforeEach(() => {
    mockedUseInvoices.mockReturnValue({
      data: {
        results: [
          { id: "inv-1", invoice_number: "INV-1", tenant_name: "John Kamau", balance: "5000.00" },
          { id: "inv-2", invoice_number: "INV-2", tenant_name: "Jane Wanjiru", balance: "0.00" },
        ],
      },
    } as never);
    mockedUseAllocateToInvoice.mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue({}),
      isPending: false,
      error: null,
    } as never);
  });

  it("only lists invoices with an outstanding balance", () => {
    render(<AllocateToInvoiceForm paymentId="payment-1" onSuccess={vi.fn()} />);

    expect(screen.getByText(/INV-1 - John Kamau/)).toBeInTheDocument();
    expect(screen.queryByText(/INV-2 - Jane Wanjiru/)).not.toBeInTheDocument();
  });

  it("submits the invoice id and amount", async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockedUseAllocateToInvoice.mockReturnValue({ mutateAsync, isPending: false, error: null } as never);
    const onSuccess = vi.fn();
    const user = userEvent.setup();

    render(<AllocateToInvoiceForm paymentId="payment-1" onSuccess={onSuccess} />);

    await user.selectOptions(screen.getByLabelText(/^invoice/i), "inv-1");
    await user.type(screen.getByLabelText(/^amount/i), "5000");
    await user.click(screen.getByRole("button", { name: /^allocate$/i }));

    expect(mutateAsync).toHaveBeenCalledWith({ invoice: "inv-1", amount: "5000" });
    expect(onSuccess).toHaveBeenCalled();
  });
});
