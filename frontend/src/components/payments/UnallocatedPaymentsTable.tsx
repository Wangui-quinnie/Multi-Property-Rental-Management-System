import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { components } from "@/types/api";

type UnallocatedPayment = components["schemas"]["UnallocatedPayment"];

interface UnallocatedPaymentsTableProps {
  entries: UnallocatedPayment[];
  isLoading: boolean;
}

export function UnallocatedPaymentsTable({ entries, isLoading }: UnallocatedPaymentsTableProps) {
  if (isLoading) return <TableSkeleton columns={4} />;
  if (entries.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No unallocated payments.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Reference</TableHead>
          <TableHead>Tenant</TableHead>
          <TableHead>Amount</TableHead>
          <TableHead>Unallocated</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {entries.map((entry) => (
          <TableRow key={entry.payment_id}>
            <TableCell className="font-medium">{entry.payment_reference}</TableCell>
            <TableCell>{entry.tenant_name}</TableCell>
            <TableCell>{entry.amount}</TableCell>
            <TableCell>{entry.unallocated_amount}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
