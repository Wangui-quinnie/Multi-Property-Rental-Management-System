import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { FormSelect } from "@/components/shared/FormSelect";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useApplyLateFee } from "@/hooks/useInvoices";

interface ApplyLateFeeFormProps {
  invoiceId: string;
  onSuccess: () => void;
}

/**
 * Only rendered for an overdue invoice with an outstanding balance - the
 * backend rejects (400) applying a late fee to a non-overdue invoice, or
 * a second one on the same day (apps/billing/services/penalty.py
 * apply_late_fee), so those errors surface inline if hit anyway.
 */
export function ApplyLateFeeForm({ invoiceId, onSuccess }: ApplyLateFeeFormProps) {
  const [feeType, setFeeType] = useState<"FIXED" | "PERCENTAGE">("FIXED");
  const [value, setValue] = useState("");

  const applyLateFee = useApplyLateFee(invoiceId);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await applyLateFee.mutateAsync({ fee_type: feeType, value });
    toast.add({ title: "Late fee applied.", type: "success" });
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <h3 className="font-medium">Apply late fee</h3>
      {getErrorMessage(applyLateFee.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(applyLateFee.error)}</AlertDescription>
        </Alert>
      )}

      <FormSelect
        label="Fee type"
        id="fee_type"
        value={feeType}
        onChange={(e) => setFeeType(e.target.value as "FIXED" | "PERCENTAGE")}
      >
        <option value="FIXED">Fixed amount</option>
        <option value="PERCENTAGE">Percentage of balance</option>
      </FormSelect>

      <FormInput
        label={feeType === "PERCENTAGE" ? "Percentage" : "Amount"}
        id="fee_value"
        type="number"
        min="0"
        step="0.01"
        required
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      <Button type="submit" disabled={applyLateFee.isPending}>
        {applyLateFee.isPending ? "Applying..." : "Apply late fee"}
      </Button>
    </form>
  );
}
