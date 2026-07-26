import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ActivateOccupancyForm } from "./ActivateOccupancyForm";
import { useActivateOccupancy } from "@/hooks/useOccupancy";

vi.mock("@/hooks/useOccupancy");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseActivateOccupancy = vi.mocked(useActivateOccupancy);

describe("ActivateOccupancyForm", () => {
  beforeEach(() => {
    mockedUseActivateOccupancy.mockReset();
  });

  it("submits with the lease id and an omitted move-in date when left blank", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseActivateOccupancy.mockReturnValue({
      mutateAsync,
      isPending: false,
      error: null,
    } as never);

    const onSuccess = vi.fn();
    const user = userEvent.setup();

    render(<ActivateOccupancyForm leaseId="lease-1" onSuccess={onSuccess} />);
    await user.click(screen.getByRole("button", { name: /activate occupancy/i }));

    expect(mutateAsync).toHaveBeenCalledWith({ lease: "lease-1", move_in_date: undefined });
    expect(onSuccess).toHaveBeenCalled();
  });

  it("submits a specified move-in date", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseActivateOccupancy.mockReturnValue({
      mutateAsync,
      isPending: false,
      error: null,
    } as never);

    const user = userEvent.setup();
    render(<ActivateOccupancyForm leaseId="lease-1" onSuccess={vi.fn()} />);

    await user.type(screen.getByLabelText("Move-in date"), "2026-03-01");
    await user.click(screen.getByRole("button", { name: /activate occupancy/i }));

    expect(mutateAsync).toHaveBeenCalledWith({ lease: "lease-1", move_in_date: "2026-03-01" });
  });
});