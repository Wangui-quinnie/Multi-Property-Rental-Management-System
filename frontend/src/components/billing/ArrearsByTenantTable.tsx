import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { ArrearsByTenant } from "@/api/invoices";

interface ArrearsByTenantTableProps {
  entries: ArrearsByTenant[];
  isLoading: boolean;
}

export function ArrearsByTenantTable({ entries, isLoading }: ArrearsByTenantTableProps) {
  if (isLoading) return <TableSkeleton columns={4} />;
  if (entries.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No tenants in arrears.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Tenant</TableHead>
          <TableHead>Total arrears</TableHead>
          <TableHead>Overdue invoices</TableHead>
          <TableHead>Leases in arrears</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {entries.map((entry) => (
          <TableRow key={entry.tenant_id}>
            <TableCell className="font-medium">{entry.tenant_name}</TableCell>
            <TableCell>{entry.total_arrears}</TableCell>
            <TableCell>{entry.overdue_invoice_count}</TableCell>
            <TableCell>{entry.lease_count}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
