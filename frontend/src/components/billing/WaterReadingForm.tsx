import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import { useUnits } from "@/hooks/useUnits";
import { useBillingPeriods } from "@/hooks/useBillingPeriods";
import type {
  WaterMeterReading, WaterMeterReadingCreate, WaterMeterReadingUpdate,
} from "@/api/waterReadings";

interface WaterReadingFormProps {
  /** Present when editing an existing reading; absent when creating. */
  reading?: WaterMeterReading;
  onSubmit: (data: WaterMeterReadingCreate | WaterMeterReadingUpdate) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

/**
 * unit/billing_period are only settable at creation time
 * (WaterMeterReadingUpdateSerializer deliberately excludes both - they
 * define WHICH reading this is, not correctable fields; see
 * apps/billing/serializers/water.py).
 */
export function WaterReadingForm({ reading, onSubmit, isSubmitting, submitError }: WaterReadingFormProps) {
  const isEdit = !!reading;

  // page_size: 100 (DefaultPagination's max) so the pickers aren't
  // silently truncated to the default page of 10.
  const { data: unitsPage } = useUnits(isEdit ? undefined : { page_size: 100 });
  const { data: periodsPage } = useBillingPeriods(isEdit ? undefined : { page_size: 100 });

  const [unitId, setUnitId] = useState("");
  const [billingPeriodId, setBillingPeriodId] = useState("");
  const [previousReading, setPreviousReading] = useState(reading?.previous_reading ?? "0");
  const [currentReading, setCurrentReading] = useState(reading?.current_reading ?? "");
  const [ratePerUnit, setRatePerUnit] = useState(reading?.rate_per_unit ?? "");
  const [readingDate, setReadingDate] = useState(reading?.reading_date ?? "");

  const fieldErrors = parseFieldErrors(submitError);
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const shared = {
      previous_reading: previousReading,
      current_reading: currentReading,
      rate_per_unit: ratePerUnit,
      reading_date: readingDate,
    };

    if (isEdit) {
      await onSubmit(shared);
    } else {
      await onSubmit({ ...shared, unit: unitId, billing_period: billingPeriodId });
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
        <>
          <FormSelect
            label="Unit"
            id="unit"
            required
            value={unitId}
            onChange={(e) => setUnitId(e.target.value)}
            error={fieldErrors.unit}
          >
            <option value="">Select a unit...</option>
            {unitsPage?.results.map((u) => (
              <option key={u.id} value={u.id}>
                {u.property_name} - {u.unit_number}
              </option>
            ))}
          </FormSelect>

          <FormSelect
            label="Billing period"
            id="billing_period"
            required
            value={billingPeriodId}
            onChange={(e) => setBillingPeriodId(e.target.value)}
            error={fieldErrors.billing_period}
          >
            <option value="">Select a billing period...</option>
            {periodsPage?.results.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </FormSelect>
        </>
      )}

      <FormInput
        label="Previous reading"
        id="previous_reading"
        type="number"
        min="0"
        step="0.01"
        required
        value={previousReading}
        onChange={(e) => setPreviousReading(e.target.value)}
        error={fieldErrors.previous_reading}
      />

      <FormInput
        label="Current reading"
        id="current_reading"
        type="number"
        min="0"
        step="0.01"
        required
        value={currentReading}
        onChange={(e) => setCurrentReading(e.target.value)}
        error={fieldErrors.current_reading}
      />

      <FormInput
        label="Rate per unit"
        id="rate_per_unit"
        type="number"
        min="0"
        step="0.01"
        required
        value={ratePerUnit}
        onChange={(e) => setRatePerUnit(e.target.value)}
        error={fieldErrors.rate_per_unit}
      />

      <FormInput
        label="Reading date"
        id="reading_date"
        type="date"
        required
        value={readingDate}
        onChange={(e) => setReadingDate(e.target.value)}
        error={fieldErrors.reading_date}
      />

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : isEdit ? "Save changes" : "Add reading"}
      </Button>
    </form>
  );
}
