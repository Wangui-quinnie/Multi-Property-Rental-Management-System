import { useState } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ReceiptDialog } from "@/components/payments/ReceiptDialog";
import type { Payment } from "@/api/payments";

interface TenantPaymentDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  payment: Payment;
}

// Read-only variant of payments/PaymentDetailDialog for the Tenant Portal -
// deliberately omits Allocate/Remove allocation/Reconcile (Admin/Landlord-only
// actions); "View receipt" reuses ReceiptDialog as-is since it's already
// fully read-only.
export function TenantPaymentDetailDialog({ open, onOpenChange, payment }: TenantPaymentDetailDialogProps) {
  const [viewingReceipt, setViewingReceipt] = useState(false);

  const canViewReceipt = payment.status === "CONFIRMED";

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Payment {payment.payment_reference}</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <p className="text-muted-foreground">Amount</p>
              <p>{payment.amount}</p>
              <p className="text-muted-foreground">Unallocated</p>
              <p>{payment.unallocated_amount}</p>
              <p className="text-muted-foreground">Status</p>
              <p>{payment.status}</p>
              <p className="text-muted-foreground">Reconciled</p>
              <p>{payment.is_reconciled ? "Yes" : "No"}</p>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice</TableHead>
                  <TableHead>Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payment.allocations.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={2} className="text-center text-muted-foreground">
                      No allocations yet.
                    </TableCell>
                  </TableRow>
                )}
                {payment.allocations.map((allocation) => (
                  <TableRow key={allocation.id}>
                    <TableCell>{allocation.invoice_number}</TableCell>
                    <TableCell>{allocation.amount_allocated}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {canViewReceipt && (
              <Button variant="outline" onClick={() => setViewingReceipt(true)}>
                View receipt
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {viewingReceipt && (
        <ReceiptDialog
          open={viewingReceipt}
          onOpenChange={setViewingReceipt}
          paymentId={payment.id}
        />
      )}
    </>
  );
}
