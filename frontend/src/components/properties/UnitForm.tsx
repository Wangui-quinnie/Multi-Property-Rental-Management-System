import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import type { Unit, UnitCreate, UnitUpdate } from "@/api/properties";

interface UnitFormProps {
  /** A unit always belongs to one property, fixed at creation — this
   * form is always used in the context of a specific property (its
   * detail page), never as a standalone cross-property picker. */
  propertyId: string;
  /** Present when editing an existing unit; absent when creating. */
  unit?: Unit;
  onSubmit: (data: UnitCreate | UnitUpdate) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

export function UnitForm({ propertyId, unit, onSubmit, isSubmitting, submitError }: UnitFormProps) {
  const isEdit = !!unit;

  // unit_number is only settable at creation time (see
  // UnitUpdateSerializer, which excludes it — a unit's number never
  // changes once assigned).
  const [unitNumber, setUnitNumber] = useState(unit?.unit_number ?? "");
  const [unitType, setUnitType] = useState(unit?.unit_type ?? "");
  const [floorNumber, setFloorNumber] = useState(
    unit?.floor_number != null ? String(unit.floor_number) : ""
  );
  const [rentAmount, setRentAmount] = useState(unit?.rent_amount ?? "");
  const [status, setStatus] = useState(unit?.status ?? "VACANT");

  const fieldErrors = parseFieldErrors(submitError);
  // See PropertyForm.tsx for why this guards the generic banner - plain
  // DRF validation errors have no top-level message, so getErrorMessage
  // falls back to (and would duplicate) the first field error.
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const shared = {
      unit_type: unitType,
      floor_number: floorNumber === "" ? null : Number(floorNumber),
      rent_amount: rentAmount,
      status,
    };

    if (isEdit) {
      await onSubmit(shared as UnitUpdate);
    } else {
      await onSubmit({ property: propertyId, unit_number: unitNumber, ...shared } as UnitCreate);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!hasFieldErrors && getErrorMessage(submitError, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(submitError)}</AlertDescription>
        </Alert>
      )}

      {!isEdit && (
        <FormInput
          label="Unit number"
          id="unit_number"
          required
          value={unitNumber}
          onChange={(e) => setUnitNumber(e.target.value)}
          error={fieldErrors.unit_number}
        />
      )}

      <FormInput
        label="Unit type"
        id="unit_type"
        placeholder="e.g. Bedsitter, 1BR, 2BR"
        value={unitType}
        onChange={(e) => setUnitType(e.target.value)}
        error={fieldErrors.unit_type}
      />

      <FormInput
        label="Floor number"
        id="floor_number"
        type="number"
        value={floorNumber}
        onChange={(e) => setFloorNumber(e.target.value)}
        error={fieldErrors.floor_number}
      />

      <FormInput
        label="Rent amount"
        id="rent_amount"
        type="number"
        min="0"
        step="0.01"
        required
        value={rentAmount}
        onChange={(e) => setRentAmount(e.target.value)}
        error={fieldErrors.rent_amount}
      />

      <FormSelect
        label="Status"
        id="status"
        value={status}
        onChange={(e) => setStatus(e.target.value as NonNullable<Unit["status"]>)}
        error={fieldErrors.status}
      >
        <option value="VACANT">Vacant</option>
        <option value="OCCUPIED">Occupied</option>
        <option value="MAINTENANCE">Maintenance</option>
        <option value="INACTIVE">Inactive</option>
      </FormSelect>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : isEdit ? "Save changes" : "Add unit"}
      </Button>
    </form>
  );
}