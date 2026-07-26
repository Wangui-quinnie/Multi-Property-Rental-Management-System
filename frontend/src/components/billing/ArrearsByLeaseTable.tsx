import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { ArrearsByLease } from "@/api/invoices";

interface ArrearsByLeaseTableProps {
  entries: ArrearsByLease[];
  isLoading: boolean;
}

export function ArrearsByLeaseTable({ entries, isLoading }: ArrearsByLeaseTableProps) {
  if (isLoading) return <TableSkeleton columns={5} />;
  if (entries.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No leases in arrears.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Tenant</TableHead>
          <TableHead>Unit</TableHead>
          <TableHead>Total arrears</TableHead>
          <TableHead>Overdue invoices</TableHead>
          <TableHead>Days in arrears</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {entries.map((entry) => (
          <TableRow key={entry.lease_id}>
            <TableCell className="font-medium">{entry.tenant_name}</TableCell>
            <TableCell>{entry.property_name} - {entry.unit_number}</TableCell>
            <TableCell>{entry.total_arrears}</TableCell>
            <TableCell>{entry.overdue_invoice_count}</TableCell>
            <TableCell>{entry.days_in_arrears}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
