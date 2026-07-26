import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { components } from "@/types/api";

type StalePendingMpesa = components["schemas"]["StalePendingMpesa"];

interface StalePendingMpesaTableProps {
  entries: StalePendingMpesa[];
  isLoading: boolean;
}

export function StalePendingMpesaTable({ entries, isLoading }: StalePendingMpesaTableProps) {
  if (isLoading) return <TableSkeleton columns={5} />;
  if (entries.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No stale pending M-Pesa transactions.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Tenant</TableHead>
          <TableHead>Phone</TableHead>
          <TableHead>Amount</TableHead>
          <TableHead>Checkout ID</TableHead>
          <TableHead>Hours pending</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {entries.map((entry) => (
          <TableRow key={entry.transaction_id}>
            <TableCell className="font-medium">{entry.tenant_name}</TableCell>
            <TableCell>{entry.phone_number}</TableCell>
            <TableCell>{entry.amount}</TableCell>
            <TableCell>{entry.checkout_request_id}</TableCell>
            <TableCell>{entry.hours_pending}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
