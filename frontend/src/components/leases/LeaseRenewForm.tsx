import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { getErrorMessage } from "@/api/errors";
import { useRenewLease } from "@/hooks/useLeases";
import { toast } from "@/components/ui/toast";
import type { Lease } from "@/api/leases";

interface LeaseRenewFormProps {
  lease: Lease;
  onSuccess: () => void;
}

// Pre-fills rent/deposit/billing_day from the current lease since a
// renewal usually carries the same terms forward - all remain editable.
export function LeaseRenewForm({ lease, onSuccess }: LeaseRenewFormProps) {
  const [newStartDate, setNewStartDate] = useState("");
  const [newEndDate, setNewEndDate] = useState("");
  const [rentAmount, setRentAmount] = useState(lease.rent_amount);
  const [depositAmount, setDepositAmount] = useState(lease.deposit_amount);
  const [billingDay, setBillingDay] = useState(String(lease.billing_day));

  const renewLease = useRenewLease(lease.id);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await renewLease.mutateAsync({
      new_lease_start_date: newStartDate,
      new_lease_end_date: newEndDate || null,
      rent_amount: rentAmount,
      deposit_amount: depositAmount,
      billing_day: Number(billingDay),
    });
    toast.add({ title: "Lease renewed.", type: "success" });
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <h3 className="font-medium">Renew lease</h3>
      {getErrorMessage(renewLease.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(renewLease.error)}</AlertDescription>
        </Alert>
      )}

      <FormInput
        label="New lease start date"
        id="new_lease_start_date"
        type="date"
        required
        value={newStartDate}
        onChange={(e) => setNewStartDate(e.target.value)}
      />

      <FormInput
        label="New lease end date"
        id="new_lease_end_date"
        type="date"
        value={newEndDate}
        onChange={(e) => setNewEndDate(e.target.value)}
      />

      <FormInput
        label="Rent amount"
        id="renew_rent_amount"
        type="number"
        min="0"
        step="0.01"
        required
        value={rentAmount}
        onChange={(e) => setRentAmount(e.target.value)}
      />

      <FormInput
        label="Deposit amount"
        id="renew_deposit_amount"
        type="number"
        min="0"
        step="0.01"
        value={depositAmount}
        onChange={(e) => setDepositAmount(e.target.value)}
      />

      <FormInput
        label="Billing day"
        id="renew_billing_day"
        type="number"
        min="1"
        max="31"
        required
        value={billingDay}
        onChange={(e) => setBillingDay(e.target.value)}
      />

      <Button type="submit" disabled={renewLease.isPending}>
        {renewLease.isPending ? "Renewing..." : "Renew lease"}
      </Button>
    </form>
  );
}