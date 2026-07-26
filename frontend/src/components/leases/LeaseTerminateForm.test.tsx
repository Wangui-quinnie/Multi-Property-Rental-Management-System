import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LeaseTerminateForm } from "./LeaseTerminateForm";
import { useTerminateLease } from "@/hooks/useLeases";

vi.mock("@/hooks/useLeases");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseTerminateLease = vi.mocked(useTerminateLease);

describe("LeaseTerminateForm", () => {
  beforeEach(() => {
    mockedUseTerminateLease.mockReset();
  });

  it("submits with an omitted termination date when left blank", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseTerminateLease.mockReturnValue({
      mutateAsync,
      isPending: false,
      error: null,
    } as never);

    const onSuccess = vi.fn();
    const user = userEvent.setup();

    render(<LeaseTerminateForm leaseId="lease-1" onSuccess={onSuccess} />);
    await user.click(screen.getByRole("button", { name: /terminate lease/i }));

    expect(mutateAsync).toHaveBeenCalledWith({ termination_date: undefined });
    expect(onSuccess).toHaveBeenCalled();
  });

  it("submits a specified termination date", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseTerminateLease.mockReturnValue({
      mutateAsync,
      isPending: false,
      error: null,
    } as never);

    const user = userEvent.setup();
    render(<LeaseTerminateForm leaseId="lease-1" onSuccess={vi.fn()} />);

    await user.type(screen.getByLabelText("Termination date"), "2026-06-15");
    await user.click(screen.getByRole("button", { name: /terminate lease/i }));

    expect(mutateAsync).toHaveBeenCalledWith({ termination_date: "2026-06-15" });
  });
});