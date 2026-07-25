import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { UnitForm } from "./UnitForm";
import type { Unit } from "@/api/properties";

const sampleUnit: Unit = {
  id: "unit-1",
  property: "property-1",
  property_name: "Sunset Apartments",
  landlord_name: "Ada Landlord",
  unit_number: "A1",
  unit_type: "1BR",
  floor_number: 2,
  rent_amount: "15000.00",
  status: "VACANT",
  is_archived: false,
  archived_at: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("UnitForm", () => {
  it("shows the unit number field when creating", () => {
    render(
      <UnitForm propertyId="property-1" onSubmit={vi.fn()} isSubmitting={false} submitError={null} />
    );
    // Required field, so its accessible name is actually "Unit number *"
    // (see FormField's required asterisk) - match with a regex rather
    // than an exact string, same convention used in Login.test.tsx.
    expect(screen.getByLabelText(/^unit number/i)).toBeInTheDocument();
  });

  it("hides the unit number field when editing and pre-fills the rest", () => {
    render(
      <UnitForm
        propertyId="property-1"
        unit={sampleUnit}
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={null}
      />
    );

    expect(screen.queryByLabelText(/^unit number/i)).not.toBeInTheDocument();
    expect(screen.getByLabelText("Unit type")).toHaveValue("1BR");
    expect(screen.getByLabelText(/^rent amount/i)).toHaveValue(15000);
  });

  it("submits property + unit_number + shared fields when creating", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(
      <UnitForm propertyId="property-1" onSubmit={onSubmit} isSubmitting={false} submitError={null} />
    );

    await user.type(screen.getByLabelText(/^unit number/i), "B2");
    await user.type(screen.getByLabelText(/^rent amount/i), "12000");
    await user.click(screen.getByRole("button", { name: /add unit/i }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ property: "property-1", unit_number: "B2", rent_amount: "12000" })
    );
  });

  it("submits without property/unit_number when editing", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(
      <UnitForm
        propertyId="property-1"
        unit={sampleUnit}
        onSubmit={onSubmit}
        isSubmitting={false}
        submitError={null}
      />
    );

    await user.click(screen.getByRole("button", { name: /save changes/i }));

    const submitted = onSubmit.mock.calls[0][0];
    expect(submitted).not.toHaveProperty("property");
    expect(submitted).not.toHaveProperty("unit_number");
    expect(submitted.rent_amount).toBe("15000.00");
  });
});