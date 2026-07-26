import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { MpesaTransaction } from "@/api/mpesa";

interface MpesaTransactionTableProps {
  transactions: MpesaTransaction[];
  isLoading: boolean;
}

// Read-only - transactions are only ever created via the initiate
// action and only ever transitioned by Safaricom's callback, never
// edited directly (see MpesaTransactionViewSet).
export function MpesaTransactionTable({ transactions, isLoading }: MpesaTransactionTableProps) {
  if (isLoading) return <TableSkeleton columns={6} />;
  if (transactions.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No M-Pesa transactions yet.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Tenant</TableHead>
          <TableHead>Phone</TableHead>
          <TableHead>Amount</TableHead>
          <TableHead>Checkout ID</TableHead>
          <TableHead>Receipt #</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.map((txn) => (
          <TableRow key={txn.id}>
            <TableCell className="font-medium">{txn.tenant_name}</TableCell>
            <TableCell>{txn.phone_number}</TableCell>
            <TableCell>{txn.amount}</TableCell>
            <TableCell>{txn.checkout_request_id}</TableCell>
            <TableCell>{txn.mpesa_receipt_number || "-"}</TableCell>
            <TableCell>{txn.status}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
