import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ChangePasswordForm } from "./ChangePasswordForm";
import { useChangePassword } from "@/hooks/useProfile";
import { toast } from "@/components/ui/toast";

vi.mock("@/hooks/useProfile");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseChangePassword = vi.mocked(useChangePassword);
const mockedToast = vi.mocked(toast.add);

describe("ChangePasswordForm", () => {
  beforeEach(() => {
    mockedUseChangePassword.mockReset();
    mockedToast.mockReset();
  });

  it("submits current/new/confirm password fields", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseChangePassword.mockReturnValue({ mutateAsync, isPending: false, error: null } as never);

    const user = userEvent.setup();
    render(<ChangePasswordForm />);

    await user.type(screen.getByLabelText(/^current password/i), "oldpass123");
    await user.type(screen.getByLabelText(/^new password/i), "newpass456");
    await user.type(screen.getByLabelText(/^confirm new password/i), "newpass456");
    await user.click(screen.getByRole("button", { name: /change password/i }));

    expect(mutateAsync).toHaveBeenCalledWith({
      current_password: "oldpass123",
      new_password: "newpass456",
      confirm_password: "newpass456",
    });
  });

  it("shows an error toast without submitting when the confirmation doesn't match", async () => {
    const mutateAsync = vi.fn();
    mockedUseChangePassword.mockReturnValue({ mutateAsync, isPending: false, error: null } as never);

    const user = userEvent.setup();
    render(<ChangePasswordForm />);

    await user.type(screen.getByLabelText(/^current password/i), "oldpass123");
    await user.type(screen.getByLabelText(/^new password/i), "newpass456");
    await user.type(screen.getByLabelText(/^confirm new password/i), "doesnotmatch");
    await user.click(screen.getByRole("button", { name: /change password/i }));

    expect(mutateAsync).not.toHaveBeenCalled();
    expect(mockedToast).toHaveBeenCalledWith(
      expect.objectContaining({ type: "error" })
    );
  });
});
