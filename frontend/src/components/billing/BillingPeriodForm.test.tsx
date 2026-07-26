import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { BillingPeriodForm } from "./BillingPeriodForm";
import type { BillingPeriod } from "@/api/billingPeriods";

const samplePeriod: BillingPeriod = {
  id: "period-1",
  name: "January 2026",
  start_date: "2026-01-01",
  end_date: "2026-01-31",
  due_date: "2026-01-05",
  status: "OPEN",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("BillingPeriodForm", () => {
  it("defaults status to OPEN when creating", () => {
    render(<BillingPeriodForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);

    expect(screen.getByLabelText("Status")).toHaveValue("OPEN");
  });

  it("pre-fills fields when editing", () => {
    render(
      <BillingPeriodForm
        period={samplePeriod}
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={null}
      />
    );

    expect(screen.getByLabelText(/^name/i)).toHaveValue("January 2026");
    expect(screen.getByLabelText(/^start date/i)).toHaveValue("2026-01-01");
    expect(screen.getByLabelText(/^end date/i)).toHaveValue("2026-01-31");
    expect(screen.getByLabelText(/^due date/i)).toHaveValue("2026-01-05");
  });

  it("submits the entered shape", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(<BillingPeriodForm onSubmit={onSubmit} isSubmitting={false} submitError={null} />);

    await user.type(screen.getByLabelText(/^name/i), "February 2026");
    await user.type(screen.getByLabelText(/^start date/i), "2026-02-01");
    await user.type(screen.getByLabelText(/^end date/i), "2026-02-28");
    await user.type(screen.getByLabelText(/^due date/i), "2026-02-05");
    await user.click(screen.getByRole("button", { name: /create billing period/i }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        name: "February 2026",
        start_date: "2026-02-01",
        end_date: "2026-02-28",
        due_date: "2026-02-05",
        status: "OPEN",
      })
    );
  });

  it("shows 'Save changes' as the submit label when editing", () => {
    render(
      <BillingPeriodForm
        period={samplePeriod}
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={null}
      />
    );

    expect(screen.getByRole("button", { name: /save changes/i })).toBeInTheDocument();
  });
});
