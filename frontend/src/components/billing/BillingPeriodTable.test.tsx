import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { BillingPeriodTable } from "./BillingPeriodTable";
import { useGenerateRentInvoices } from "@/hooks/useInvoices";
import type { BillingPeriod } from "@/api/billingPeriods";

vi.mock("@/hooks/useInvoices");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseGenerateRentInvoices = vi.mocked(useGenerateRentInvoices);

const openPeriod: BillingPeriod = {
  id: "period-1",
  name: "January 2026",
  start_date: "2026-01-01",
  end_date: "2026-01-31",
  due_date: "2026-01-05",
  status: "OPEN",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const closedPeriod: BillingPeriod = { ...openPeriod, id: "period-2", status: "CLOSED" };

describe("BillingPeriodTable", () => {
  beforeEach(() => {
    mockedUseGenerateRentInvoices.mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue([]),
      isPending: false,
    } as never);
  });

  it("renders a row with the period's details", () => {
    render(
      <BillingPeriodTable
        periods={[openPeriod]}
        isLoading={false}
        canWrite={false}
        onEdit={vi.fn()}
        onApplyLateFees={vi.fn()}
      />
    );

    expect(screen.getByText("January 2026")).toBeInTheDocument();
    expect(screen.getByText("OPEN")).toBeInTheDocument();
  });

  it("only shows the Edit button when canWrite is true", () => {
    const { rerender } = render(
      <BillingPeriodTable
        periods={[openPeriod]}
        isLoading={false}
        canWrite={false}
        onEdit={vi.fn()}
        onApplyLateFees={vi.fn()}
      />
    );
    expect(screen.queryByRole("button", { name: /^edit/i })).not.toBeInTheDocument();

    rerender(
      <BillingPeriodTable
        periods={[openPeriod]}
        isLoading={false}
        canWrite={true}
        onEdit={vi.fn()}
        onApplyLateFees={vi.fn()}
      />
    );
    expect(screen.getByRole("button", { name: /^edit/i })).toBeInTheDocument();
  });

  it("disables 'Generate rent invoices' for a CLOSED period", () => {
    render(
      <BillingPeriodTable
        periods={[closedPeriod]}
        isLoading={false}
        canWrite={false}
        onEdit={vi.fn()}
        onApplyLateFees={vi.fn()}
      />
    );

    expect(screen.getByRole("button", { name: /generate rent invoices/i })).toBeDisabled();
  });

  it("enables 'Generate rent invoices' for an OPEN period and calls the mutation", async () => {
    const mutateAsync = vi.fn().mockResolvedValue([{ id: "inv-1" }]);
    mockedUseGenerateRentInvoices.mockReturnValue({ mutateAsync, isPending: false } as never);
    const user = userEvent.setup();

    render(
      <BillingPeriodTable
        periods={[openPeriod]}
        isLoading={false}
        canWrite={false}
        onEdit={vi.fn()}
        onApplyLateFees={vi.fn()}
      />
    );

    const button = screen.getByRole("button", { name: /generate rent invoices/i });
    expect(button).not.toBeDisabled();

    await user.click(button);
    expect(mutateAsync).toHaveBeenCalledWith({ billing_period: "period-1" });
  });

  it("calls onApplyLateFees with the period when clicked", async () => {
    const onApplyLateFees = vi.fn();
    const user = userEvent.setup();

    render(
      <BillingPeriodTable
        periods={[openPeriod]}
        isLoading={false}
        canWrite={false}
        onEdit={vi.fn()}
        onApplyLateFees={onApplyLateFees}
      />
    );

    await user.click(screen.getByRole("button", { name: /apply late fees/i }));
    expect(onApplyLateFees).toHaveBeenCalledWith(openPeriod);
  });

  it("shows an empty-state message when there are no periods", () => {
    render(
      <BillingPeriodTable
        periods={[]}
        isLoading={false}
        canWrite={false}
        onEdit={vi.fn()}
        onApplyLateFees={vi.fn()}
      />
    );
    expect(screen.getByText("No billing periods yet.")).toBeInTheDocument();
  });
});
