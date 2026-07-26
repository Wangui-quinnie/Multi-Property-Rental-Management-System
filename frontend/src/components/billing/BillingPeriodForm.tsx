import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import type { BillingPeriod, BillingPeriodWrite } from "@/api/billingPeriods";

interface BillingPeriodFormProps {
  /** Present when editing an existing period; absent when creating. */
  period?: BillingPeriod;
  onSubmit: (data: BillingPeriodWrite) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

export function BillingPeriodForm({ period, onSubmit, isSubmitting, submitError }: BillingPeriodFormProps) {
  const isEdit = !!period;

  const [name, setName] = useState(period?.name ?? "");
  const [startDate, setStartDate] = useState(period?.start_date ?? "");
  const [endDate, setEndDate] = useState(period?.end_date ?? "");
  const [dueDate, setDueDate] = useState(period?.due_date ?? "");
  const [status, setStatus] = useState<"OPEN" | "CLOSED">(
    (period?.status as "OPEN" | "CLOSED") ?? "OPEN"
  );

  const fieldErrors = parseFieldErrors(submitError);
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onSubmit({
      name,
      start_date: startDate,
      end_date: endDate,
      due_date: dueDate,
      status,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!hasFieldErrors && getErrorMessage(submitError, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(submitError)}</AlertDescription>
        </Alert>
      )}

      <FormInput
        label="Name"
        id="name"
        required
        value={name}
        onChange={(e) => setName(e.target.value)}
        error={fieldErrors.name}
      />

      <FormInput
        label="Start date"
        id="start_date"
        type="date"
        required
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        error={fieldErrors.start_date}
      />

      <FormInput
        label="End date"
        id="end_date"
        type="date"
        required
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
        error={fieldErrors.end_date}
      />

      <FormInput
        label="Due date"
        id="due_date"
        type="date"
        required
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
        error={fieldErrors.due_date}
      />

      <FormSelect
        label="Status"
        id="status"
        value={status}
        onChange={(e) => setStatus(e.target.value as "OPEN" | "CLOSED")}
        error={fieldErrors.status}
      >
        <option value="OPEN">Open</option>
        <option value="CLOSED">Closed</option>
      </FormSelect>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : isEdit ? "Save changes" : "Create billing period"}
      </Button>
    </form>
  );
}
