import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import { useTenants } from "@/hooks/useTenants";
import { useUnits } from "@/hooks/useUnits";
import type { Lease, LeaseCreate, LeaseUpdate } from "@/api/leases";

interface LeaseFormProps {
  /** Present when editing an existing lease; absent when creating. */
  lease?: Lease;
  onSubmit: (data: LeaseCreate | LeaseUpdate) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

/**
 * tenant/unit are only settable at creation time (LeaseUpdateSerializer
 * excludes both - reassigning a lease to a different tenant/unit isn't
 * an "update," it's a new lease). Editing's `status` is deliberately
 * restricted to ACTIVE/CANCELLED - ending a lease only ever happens
 * via the dedicated Terminate action (see api/leases.ts).
 */
export function LeaseForm({ lease, onSubmit, isSubmitting, submitError }: LeaseFormProps) {
  const isEdit = !!lease;

  // page_size: 100 (DefaultPagination's max) so the pickers aren't
  // silently truncated to the default page of 10.
  const { data: tenantsPage } = useTenants(isEdit ? undefined : { page_size: 100 });
  const { data: unitsPage } = useUnits(isEdit ? undefined : { page_size: 100 });

  const [tenantId, setTenantId] = useState("");
  const [unitId, setUnitId] = useState("");
  const [startDate, setStartDate] = useState(lease?.lease_start_date ?? "");
  const [endDate, setEndDate] = useState(lease?.lease_end_date ?? "");
  const [rentAmount, setRentAmount] = useState(lease?.rent_amount ?? "");
  const [depositAmount, setDepositAmount] = useState(lease?.deposit_amount ?? "");
  const [billingDay, setBillingDay] = useState(String(lease?.billing_day ?? 1));
  const [status, setStatus] = useState<"ACTIVE" | "CANCELLED">(
    (lease?.status as "ACTIVE" | "CANCELLED") ?? "ACTIVE"
  );

  const fieldErrors = parseFieldErrors(submitError);
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const shared = {
      lease_start_date: startDate,
      lease_end_date: endDate || null,
      rent_amount: rentAmount,
      deposit_amount: depositAmount,
      billing_day: Number(billingDay),
    };

    if (isEdit) {
      await onSubmit({ ...shared, status });
    } else {
      await onSubmit({ ...shared, tenant: tenantId, unit: unitId });
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
            label="Tenant"
            id="tenant"
            required
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            error={fieldErrors.tenant}
          >
            <option value="">Select a tenant...</option>
            {tenantsPage?.results.map((t) => (
              <option key={t.id} value={t.id}>
                {t.full_name || t.email}
              </option>
            ))}
          </FormSelect>

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
        </>
      )}

      <FormInput
        label="Lease start date"
        id="lease_start_date"
        type="date"
        required
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        error={fieldErrors.lease_start_date}
      />

      <FormInput
        label="Lease end date"
        id="lease_end_date"
        type="date"
        value={endDate ?? ""}
        onChange={(e) => setEndDate(e.target.value)}
        error={fieldErrors.lease_end_date}
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

      <FormInput
        label="Deposit amount"
        id="deposit_amount"
        type="number"
        min="0"
        step="0.01"
        value={depositAmount}
        onChange={(e) => setDepositAmount(e.target.value)}
        error={fieldErrors.deposit_amount}
      />

      <FormInput
        label="Billing day"
        id="billing_day"
        type="number"
        min="1"
        max="31"
        required
        value={billingDay}
        onChange={(e) => setBillingDay(e.target.value)}
        error={fieldErrors.billing_day}
      />

      {isEdit && (
        <FormSelect
          label="Status"
          id="status"
          value={status}
          onChange={(e) => setStatus(e.target.value as "ACTIVE" | "CANCELLED")}
          error={fieldErrors.status}
        >
          <option value="ACTIVE">Active</option>
          <option value="CANCELLED">Cancelled</option>
        </FormSelect>
      )}

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : isEdit ? "Save changes" : "Create lease"}
      </Button>
    </form>
  );
}