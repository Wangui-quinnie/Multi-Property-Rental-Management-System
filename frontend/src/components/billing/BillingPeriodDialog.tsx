import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { BillingPeriodForm } from "@/components/billing/BillingPeriodForm";
import { useCreateBillingPeriod, useUpdateBillingPeriod } from "@/hooks/useBillingPeriods";
import { toast } from "@/components/ui/toast";
import type { BillingPeriod, BillingPeriodWrite } from "@/api/billingPeriods";

interface BillingPeriodDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Present when editing an existing period; absent when creating. */
  period?: BillingPeriod;
}

export function BillingPeriodDialog({ open, onOpenChange, period }: BillingPeriodDialogProps) {
  const createBillingPeriod = useCreateBillingPeriod();
  const updateBillingPeriod = useUpdateBillingPeriod(period?.id ?? "");

  const mutation = period ? updateBillingPeriod : createBillingPeriod;

  async function handleSubmit(data: BillingPeriodWrite) {
    await mutation.mutateAsync(data);
    toast.add({ title: period ? "Billing period updated." : "Billing period created.", type: "success" });
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{period ? "Edit billing period" : "New billing period"}</DialogTitle>
        </DialogHeader>
        <BillingPeriodForm
          period={period}
          onSubmit={handleSubmit}
          isSubmitting={mutation.isPending}
          submitError={mutation.error}
        />
      </DialogContent>
    </Dialog>
  );
}
