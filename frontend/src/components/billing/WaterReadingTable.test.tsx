import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { WaterReadingTable } from "./WaterReadingTable";
import { useApplyWaterCharge, useDeleteWaterReading } from "@/hooks/useWaterReadings";
import type { WaterMeterReading } from "@/api/waterReadings";

vi.mock("@/hooks/useWaterReadings");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseApplyWaterCharge = vi.mocked(useApplyWaterCharge);
const mockedUseDeleteWaterReading = vi.mocked(useDeleteWaterReading);

const unbilledReading: WaterMeterReading = {
  id: "reading-1",
  unit: "unit-1",
  unit_number: "A1",
  property_name: "Sunset Apartments",
  billing_period: "period-1",
  billing_period_name: "January 2026",
  previous_reading: "100.00",
  current_reading: "150.00",
  units_consumed: "50.00",
  rate_per_unit: "50.00",
  amount: "2500.00",
  reading_date: "2026-01-31",
  invoice_item: null,
  is_billed: false,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const billedReading: WaterMeterReading = { ...unbilledReading, id: "reading-2", is_billed: true };

describe("WaterReadingTable", () => {
  beforeEach(() => {
    mockedUseApplyWaterCharge.mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue(unbilledReading),
      isPending: false,
    } as never);
    mockedUseDeleteWaterReading.mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue(undefined),
      isPending: false,
    } as never);
  });

  it("renders a row with the reading's details", () => {
    render(<WaterReadingTable readings={[unbilledReading]} isLoading={false} onEdit={vi.fn()} />);

    expect(screen.getByText("Sunset Apartments - A1")).toBeInTheDocument();
    expect(screen.getByText("January 2026")).toBeInTheDocument();
  });

  it("shows Apply charge/Delete only for unbilled readings", () => {
    render(
      <WaterReadingTable readings={[unbilledReading, billedReading]} isLoading={false} onEdit={vi.fn()} />
    );

    expect(screen.getAllByRole("button", { name: /^edit/i })).toHaveLength(2);
    expect(screen.getAllByRole("button", { name: /apply charge/i })).toHaveLength(1);
    expect(screen.getAllByRole("button", { name: /^delete/i })).toHaveLength(1);
  });

  it("calls onEdit with the reading when Edit is clicked", async () => {
    const onEdit = vi.fn();
    const user = userEvent.setup();
    render(<WaterReadingTable readings={[unbilledReading]} isLoading={false} onEdit={onEdit} />);

    await user.click(screen.getByRole("button", { name: /^edit/i }));
    expect(onEdit).toHaveBeenCalledWith(unbilledReading);
  });

  it("applies the water charge when clicked", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(unbilledReading);
    mockedUseApplyWaterCharge.mockReturnValue({ mutateAsync, isPending: false } as never);
    const user = userEvent.setup();

    render(<WaterReadingTable readings={[unbilledReading]} isLoading={false} onEdit={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: /apply charge/i }));

    expect(mutateAsync).toHaveBeenCalledWith("reading-1");
  });

  it("shows a confirm dialog and deletes when confirmed", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockedUseDeleteWaterReading.mockReturnValue({ mutateAsync, isPending: false } as never);
    const user = userEvent.setup();

    render(<WaterReadingTable readings={[unbilledReading]} isLoading={false} onEdit={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: /^delete/i }));

    expect(screen.getByText("Delete this water reading?")).toBeInTheDocument();

    // Two "Delete" buttons now exist: the row action and the dialog's
    // confirm action - the confirm action is rendered last (portalled).
    const deleteButtons = screen.getAllByRole("button", { name: /^delete$/i });
    await user.click(deleteButtons[deleteButtons.length - 1]);
    expect(mutateAsync).toHaveBeenCalledWith("reading-1");
  });

  it("shows an empty-state message when there are no readings", () => {
    render(<WaterReadingTable readings={[]} isLoading={false} onEdit={vi.fn()} />);
    expect(screen.getByText("No water readings yet.")).toBeInTheDocument();
  });
});
