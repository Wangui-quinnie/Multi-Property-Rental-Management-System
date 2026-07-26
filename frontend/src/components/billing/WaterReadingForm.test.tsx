import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { WaterReadingForm } from "./WaterReadingForm";
import { useUnits } from "@/hooks/useUnits";
import { useBillingPeriods } from "@/hooks/useBillingPeriods";
import type { WaterMeterReading } from "@/api/waterReadings";

vi.mock("@/hooks/useUnits");
vi.mock("@/hooks/useBillingPeriods");

const mockedUseUnits = vi.mocked(useUnits);
const mockedUseBillingPeriods = vi.mocked(useBillingPeriods);

const sampleReading: WaterMeterReading = {
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

describe("WaterReadingForm", () => {
  beforeEach(() => {
    mockedUseUnits.mockReturnValue({
      data: { results: [{ id: "unit-1", unit_number: "A1", property_name: "Sunset Apartments" }] },
    } as never);
    mockedUseBillingPeriods.mockReturnValue({
      data: { results: [{ id: "period-1", name: "January 2026" }] },
    } as never);
  });

  it("shows unit/billing period pickers when creating", () => {
    render(<WaterReadingForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);

    expect(screen.getByLabelText(/^unit/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^billing period/i)).toBeInTheDocument();
  });

  it("hides unit/billing period pickers when editing", () => {
    render(
      <WaterReadingForm
        reading={sampleReading}
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={null}
      />
    );

    expect(screen.queryByLabelText(/^unit/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/^billing period/i)).not.toBeInTheDocument();
    expect(screen.getByLabelText(/^current reading/i)).toHaveValue(150);
  });

  it("submits the create shape with unit/billing_period ids", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(<WaterReadingForm onSubmit={onSubmit} isSubmitting={false} submitError={null} />);

    await user.selectOptions(screen.getByLabelText(/^unit/i), "unit-1");
    await user.selectOptions(screen.getByLabelText(/^billing period/i), "period-1");
    await user.type(screen.getByLabelText(/^current reading/i), "150");
    await user.type(screen.getByLabelText(/^rate per unit/i), "50");
    await user.type(screen.getByLabelText(/^reading date/i), "2026-01-31");
    await user.click(screen.getByRole("button", { name: /add reading/i }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ unit: "unit-1", billing_period: "period-1", current_reading: "150" })
    );
  });

  it("submits the update shape without unit/billing_period", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(
      <WaterReadingForm
        reading={sampleReading}
        onSubmit={onSubmit}
        isSubmitting={false}
        submitError={null}
      />
    );

    await user.click(screen.getByRole("button", { name: /save changes/i }));

    const submitted = onSubmit.mock.calls[0][0];
    expect(submitted).not.toHaveProperty("unit");
    expect(submitted).not.toHaveProperty("billing_period");
  });
});
