import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { PaymentForm } from "@/components/payments/PaymentForm";
import { useCreatePayment } from "@/hooks/usePayments";
import { toast } from "@/components/ui/toast";
import type { PaymentCreate } from "@/api/payments";

interface PaymentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PaymentDialog({ open, onOpenChange }: PaymentDialogProps) {
  const createPayment = useCreatePayment();

  async function handleSubmit(data: PaymentCreate) {
    await createPayment.mutateAsync(data);
    toast.add({ title: "Payment recorded.", type: "success" });
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Record payment</DialogTitle>
        </DialogHeader>
        <PaymentForm
          onSubmit={handleSubmit}
          isSubmitting={createPayment.isPending}
          submitError={createPayment.error}
        />
      </DialogContent>
    </Dialog>
  );
}
