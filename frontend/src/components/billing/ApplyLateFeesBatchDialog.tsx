import { useState, type FormEvent } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useApplyLateFeesBatch } from "@/hooks/useInvoices";
import type { BillingPeriod } from "@/api/billingPeriods";

interface ApplyLateFeesBatchDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  period: BillingPeriod;
}

/**
 * Applies a late fee to every overdue invoice in this billing period
 * (apps/billing/services/penalty.py apply_late_fees_for_billing_period).
 * Invoices that already got a fee today are silently skipped server-side,
 * not treated as an error - so this can be re-run safely.
 */
export function ApplyLateFeesBatchDialog({ open, onOpenChange, period }: ApplyLateFeesBatchDialogProps) {
  const [feeType, setFeeType] = useState<"FIXED" | "PERCENTAGE">("FIXED");
  const [value, setValue] = useState("");

  const applyLateFeesBatch = useApplyLateFeesBatch();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      const result = await applyLateFeesBatch.mutateAsync({
        billing_period: period.id,
        fee_type: feeType,
        value,
      });
      toast.add({
        title: `Applied late fees to ${result.late_fees_applied} invoice(s).`,
        type: "success",
      });
      onOpenChange(false);
    } catch {
      // error surfaced inline below via applyLateFeesBatch.error
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Apply late fees - {period.name}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {getErrorMessage(applyLateFeesBatch.error, "") && (
            <Alert variant="destructive">
              <AlertDescription>{getErrorMessage(applyLateFeesBatch.error)}</AlertDescription>
            </Alert>
          )}

          <FormSelect
            label="Fee type"
            id="batch_fee_type"
            value={feeType}
            onChange={(e) => setFeeType(e.target.value as "FIXED" | "PERCENTAGE")}
          >
            <option value="FIXED">Fixed amount</option>
            <option value="PERCENTAGE">Percentage of balance</option>
          </FormSelect>

          <FormInput
            label={feeType === "PERCENTAGE" ? "Percentage" : "Amount"}
            id="batch_value"
            type="number"
            min="0"
            step="0.01"
            required
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />

          <Button type="submit" disabled={applyLateFeesBatch.isPending}>
            {applyLateFeesBatch.isPending ? "Applying..." : "Apply to all overdue invoices"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
