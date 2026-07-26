import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { PaymentForm } from "./PaymentForm";
import { useTenants } from "@/hooks/useTenants";

vi.mock("@/hooks/useTenants");

const mockedUseTenants = vi.mocked(useTenants);

describe("PaymentForm", () => {
  beforeEach(() => {
    mockedUseTenants.mockReturnValue({
      data: { results: [{ id: "tenant-1", full_name: "John Kamau", email: "john@example.com" }] },
    } as never);
  });

  it("defaults payment method to CASH", () => {
    render(<PaymentForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);
    expect(screen.getByLabelText(/^payment method/i)).toHaveValue("CASH");
  });

  it("does not expose a status field", () => {
    render(<PaymentForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);
    expect(screen.queryByLabelText(/status/i)).not.toBeInTheDocument();
  });

  it("submits the entered shape without a status field", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(<PaymentForm onSubmit={onSubmit} isSubmitting={false} submitError={null} />);

    await user.selectOptions(screen.getByLabelText(/^tenant/i), "tenant-1");
    await user.type(screen.getByLabelText(/^payment reference/i), "PAY-000001");
    await user.type(screen.getByLabelText(/^amount/i), "15000");
    await user.type(screen.getByLabelText(/^payment date/i), "2026-01-05T10:00");
    await user.click(screen.getByRole("button", { name: /record payment/i }));

    const submitted = onSubmit.mock.calls[0][0];
    expect(submitted).toEqual(
      expect.objectContaining({
        tenant: "tenant-1",
        payment_reference: "PAY-000001",
        payment_method: "CASH",
        amount: "15000",
      })
    );
    expect(submitted).not.toHaveProperty("status");
  });
});
