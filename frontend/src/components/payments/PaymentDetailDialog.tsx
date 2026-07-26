import { useState } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { AllocateToInvoiceForm } from "@/components/payments/AllocateToInvoiceForm";
import { ReceiptDialog } from "@/components/payments/ReceiptDialog";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useAllocateOldest, useReconcilePayment, useRemoveAllocation } from "@/hooks/usePayments";
import type { Payment } from "@/api/payments";

interface PaymentDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  payment: Payment;
}

export function PaymentDetailDialog({ open, onOpenChange, payment }: PaymentDetailDialogProps) {
  const [viewingReceipt, setViewingReceipt] = useState(false);

  const allocateOldest = useAllocateOldest(payment.id);
  const removeAllocation = useRemoveAllocation(payment.id);
  const reconcilePayment = useReconcilePayment(payment.id);

  const canAllocateMore = Number(payment.unallocated_amount) > 0;
  const canReconcile = payment.status === "CONFIRMED" && !payment.is_reconciled;
  const canViewReceipt = payment.status === "CONFIRMED";

  async function handleAllocateOldest() {
    try {
      const result = await allocateOldest.mutateAsync();
      toast.add({
        title: `Allocated to ${result.allocations.length} invoice(s).`,
        type: "success",
      });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  async function handleRemoveAllocation(allocationId: string) {
    try {
      await removeAllocation.mutateAsync(allocationId);
      toast.add({ title: "Allocation removed.", type: "success" });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  async function handleReconcile() {
    try {
      await reconcilePayment.mutateAsync();
      toast.add({ title: "Payment reconciled.", type: "success" });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>
              Payment {payment.payment_reference} - {payment.tenant_name}
            </DialogTitle>
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
              <p>{payment.is_reconciled ? `Yes, by ${payment.reconciled_by_name}` : "No"}</p>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payment.allocations.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-muted-foreground">
                      No allocations yet.
                    </TableCell>
                  </TableRow>
                )}
                {payment.allocations.map((allocation) => (
                  <TableRow key={allocation.id}>
                    <TableCell>{allocation.invoice_number}</TableCell>
                    <TableCell>{allocation.amount_allocated}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="destructive"
                        size="sm"
                        disabled={removeAllocation.isPending}
                        onClick={() => handleRemoveAllocation(allocation.id)}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {canAllocateMore && (
              <>
                <Button
                  variant="outline"
                  disabled={allocateOldest.isPending}
                  onClick={handleAllocateOldest}
                >
                  Allocate to oldest invoices
                </Button>
                <AllocateToInvoiceForm paymentId={payment.id} onSuccess={() => undefined} />
              </>
            )}

            <div className="flex flex-wrap gap-2">
              {canReconcile && (
                <Button disabled={reconcilePayment.isPending} onClick={handleReconcile}>
                  {reconcilePayment.isPending ? "Reconciling..." : "Reconcile"}
                </Button>
              )}
              {canViewReceipt && (
                <Button variant="outline" onClick={() => setViewingReceipt(true)}>
                  View receipt
                </Button>
              )}
            </div>
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
