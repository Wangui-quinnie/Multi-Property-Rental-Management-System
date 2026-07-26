import { useState } from "react";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import { ReceiptDialog } from "@/components/payments/ReceiptDialog";
import { usePayments } from "@/hooks/usePayments";

// A receipt only exists for a CONFIRMED payment (get_receipt_data), so
// this page lists CONFIRMED payments as the "receipts" list - there's no
// separate Receipt list endpoint. Reuses ReceiptDialog directly since
// it's already fully read-only.
export function TenantReceiptsPage() {
  const [viewingPaymentId, setViewingPaymentId] = useState<string | undefined>();

  const { data: paymentsPage, isLoading } = usePayments({ status: "CONFIRMED" });
  const payments = paymentsPage?.results ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Receipts</h1>

      {isLoading ? (
        <TableSkeleton columns={4} />
      ) : payments.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">No receipts yet.</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Reference</TableHead>
              <TableHead>Method</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {payments.map((payment) => (
              <TableRow key={payment.id}>
                <TableCell className="font-medium">{payment.payment_reference}</TableCell>
                <TableCell>{payment.payment_method}</TableCell>
                <TableCell>{payment.amount}</TableCell>
                <TableCell className="text-right">
                  <Button variant="outline" size="sm" onClick={() => setViewingPaymentId(payment.id)}>
                    View receipt
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {viewingPaymentId && (
        <ReceiptDialog
          open={!!viewingPaymentId}
          onOpenChange={(open) => !open && setViewingPaymentId(undefined)}
          paymentId={viewingPaymentId}
        />
      )}
    </div>
  );
}
