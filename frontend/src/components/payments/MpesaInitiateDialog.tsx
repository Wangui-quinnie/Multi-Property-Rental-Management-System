import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { MpesaInitiateForm } from "@/components/payments/MpesaInitiateForm";

interface MpesaInitiateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MpesaInitiateDialog({ open, onOpenChange }: MpesaInitiateDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Initiate M-Pesa STK Push</DialogTitle>
        </DialogHeader>
        <MpesaInitiateForm onSuccess={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}
