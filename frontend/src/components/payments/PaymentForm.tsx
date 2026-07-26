import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage, parseFieldErrors } from "@/api/errors";
import { useTenants } from "@/hooks/useTenants";
import type { PaymentCreate } from "@/api/payments";

interface PaymentFormProps {
  onSubmit: (data: PaymentCreate) => Promise<void>;
  isSubmitting: boolean;
  submitError: unknown;
}

const PAYMENT_METHODS = ["CASH", "BANK_TRANSFER", "MPESA", "CARD", "OTHER"] as const;

/**
 * Only ever used to create a payment - Payments are immutable financial
 * records once created (PaymentViewSet has no update/destroy, see
 * apps/payments/views/payment.py). `status` is deliberately not exposed
 * here: it defaults to CONFIRMED (the model default, and the only status
 * that makes sense for a manually-recorded cash/bank/card payment) -
 * PENDING/FAILED/REVERSED are M-Pesa/correction states, not something a
 * human picks when entering a payment they just received.
 */
export function PaymentForm({ onSubmit, isSubmitting, submitError }: PaymentFormProps) {
  // page_size: 100 (DefaultPagination's max) so the picker isn't
  // silently truncated to the default page of 10.
  const { data: tenantsPage } = useTenants({ page_size: 100 });

  const [tenantId, setTenantId] = useState("");
  const [paymentReference, setPaymentReference] = useState("");
  const [paymentMethod, setPaymentMethod] = useState<(typeof PAYMENT_METHODS)[number]>("CASH");
  const [amount, setAmount] = useState("");
  const [paymentDate, setPaymentDate] = useState("");
  const [notes, setNotes] = useState("");

  const fieldErrors = parseFieldErrors(submitError);
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onSubmit({
      tenant: tenantId,
      payment_reference: paymentReference,
      payment_method: paymentMethod,
      amount,
      payment_date: paymentDate,
      notes,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!hasFieldErrors && getErrorMessage(submitError, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(submitError)}</AlertDescription>
        </Alert>
      )}

      <FormSelect
        label="Tenant"
        id="payment_tenant"
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

      <FormInput
        label="Payment reference"
        id="payment_reference"
        required
        value={paymentReference}
        onChange={(e) => setPaymentReference(e.target.value)}
        error={fieldErrors.payment_reference}
      />

      <FormSelect
        label="Payment method"
        id="payment_method"
        value={paymentMethod}
        onChange={(e) => setPaymentMethod(e.target.value as (typeof PAYMENT_METHODS)[number])}
        error={fieldErrors.payment_method}
      >
        {PAYMENT_METHODS.map((method) => (
          <option key={method} value={method}>
            {method.charAt(0) + method.slice(1).toLowerCase().replace("_", " ")}
          </option>
        ))}
      </FormSelect>

      <FormInput
        label="Amount"
        id="payment_amount"
        type="number"
        min="0.01"
        step="0.01"
        required
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        error={fieldErrors.amount}
      />

      <FormInput
        label="Payment date"
        id="payment_date"
        type="datetime-local"
        required
        value={paymentDate}
        onChange={(e) => setPaymentDate(e.target.value)}
        error={fieldErrors.payment_date}
      />

      <FormInput
        label="Notes"
        id="payment_notes"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        error={fieldErrors.notes}
      />

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Recording..." : "Record payment"}
      </Button>
    </form>
  );
}
