import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { Payment } from "@/api/payments";

interface PaymentTableProps {
  payments: Payment[];
  isLoading: boolean;
  onManage: (payment: Payment) => void;
}

export function PaymentTable({ payments, isLoading, onManage }: PaymentTableProps) {
  if (isLoading) return <TableSkeleton columns={7} />;
  if (payments.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No payments yet.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Reference</TableHead>
          <TableHead>Tenant</TableHead>
          <TableHead>Method</TableHead>
          <TableHead>Amount</TableHead>
          <TableHead>Unallocated</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Reconciled</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {payments.map((payment) => (
          <TableRow key={payment.id}>
            <TableCell className="font-medium">{payment.payment_reference}</TableCell>
            <TableCell>{payment.tenant_name}</TableCell>
            <TableCell>{payment.payment_method}</TableCell>
            <TableCell>{payment.amount}</TableCell>
            <TableCell>{payment.unallocated_amount}</TableCell>
            <TableCell>{payment.status}</TableCell>
            <TableCell>{payment.is_reconciled ? "Yes" : "No"}</TableCell>
            <TableCell className="text-right">
              <Button variant="outline" size="sm" onClick={() => onManage(payment)}>
                Manage
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
