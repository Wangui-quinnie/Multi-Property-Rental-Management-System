import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ApplyLateFeeForm } from "./ApplyLateFeeForm";
import { useApplyLateFee } from "@/hooks/useInvoices";

vi.mock("@/hooks/useInvoices");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseApplyLateFee = vi.mocked(useApplyLateFee);

describe("ApplyLateFeeForm", () => {
  beforeEach(() => {
    mockedUseApplyLateFee.mockReset();
  });

  it("submits a FIXED fee by default", async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockedUseApplyLateFee.mockReturnValue({ mutateAsync, isPending: false, error: null } as never);

    const onSuccess = vi.fn();
    const user = userEvent.setup();

    render(<ApplyLateFeeForm invoiceId="inv-1" onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText(/^amount/i), "500");
    await user.click(screen.getByRole("button", { name: /apply late fee/i }));

    expect(mutateAsync).toHaveBeenCalledWith({ fee_type: "FIXED", value: "500" });
    expect(onSuccess).toHaveBeenCalled();
  });

  it("switches the value label and submits PERCENTAGE when selected", async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockedUseApplyLateFee.mockReturnValue({ mutateAsync, isPending: false, error: null } as never);

    const user = userEvent.setup();
    render(<ApplyLateFeeForm invoiceId="inv-1" onSuccess={vi.fn()} />);

    await user.selectOptions(screen.getByLabelText(/^fee type/i), "PERCENTAGE");
    expect(screen.getByLabelText(/^percentage/i)).toBeInTheDocument();

    await user.type(screen.getByLabelText(/^percentage/i), "10");
    await user.click(screen.getByRole("button", { name: /apply late fee/i }));

    expect(mutateAsync).toHaveBeenCalledWith({ fee_type: "PERCENTAGE", value: "10" });
  });
});
