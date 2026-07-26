import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MpesaInitiateForm } from "./MpesaInitiateForm";
import { useTenants } from "@/hooks/useTenants";
import { useInitiateStkPush } from "@/hooks/useMpesa";

vi.mock("@/hooks/useTenants");
vi.mock("@/hooks/useMpesa");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseTenants = vi.mocked(useTenants);
const mockedUseInitiateStkPush = vi.mocked(useInitiateStkPush);

describe("MpesaInitiateForm", () => {
  beforeEach(() => {
    mockedUseTenants.mockReturnValue({
      data: { results: [{ id: "tenant-1", full_name: "John Kamau", email: "john@example.com" }] },
    } as never);
  });

  it("submits the tenant, phone number, and amount", async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockedUseInitiateStkPush.mockReturnValue({ mutateAsync, isPending: false, error: null } as never);
    const onSuccess = vi.fn();
    const user = userEvent.setup();

    render(<MpesaInitiateForm onSuccess={onSuccess} />);

    await user.selectOptions(screen.getByLabelText(/^tenant/i), "tenant-1");
    await user.type(screen.getByLabelText(/^phone number/i), "254712345678");
    await user.type(screen.getByLabelText(/^amount/i), "5000");
    await user.click(screen.getByRole("button", { name: /send stk push/i }));

    expect(mutateAsync).toHaveBeenCalledWith({
      tenant: "tenant-1",
      phone_number: "254712345678",
      amount: "5000",
    });
    expect(onSuccess).toHaveBeenCalled();
  });
});
