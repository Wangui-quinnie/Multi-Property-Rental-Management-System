import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { components } from "@/types/api";

type IntegrityMismatch = components["schemas"]["IntegrityMismatch"];

interface IntegrityMismatchesTableProps {
  entries: IntegrityMismatch[];
  isLoading: boolean;
}

/**
 * This should always be empty in healthy operation - it's an audit net
 * for drift that bypassed the service layer (direct DB edits, Django
 * admin, a bug), not a normal-operation check (see
 * apps/payments/services/reconciliation.py get_integrity_mismatches).
 */
export function IntegrityMismatchesTable({ entries, isLoading }: IntegrityMismatchesTableProps) {
  if (isLoading) return <TableSkeleton columns={3} />;
  if (entries.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No integrity mismatches - everything reconciles cleanly.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Type</TableHead>
          <TableHead>Reference</TableHead>
          <TableHead>Detail</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {entries.map((entry, index) => (
          <TableRow key={`${entry.type}-${entry.payment_id ?? entry.invoice_id}-${index}`}>
            <TableCell className="font-medium">{entry.type}</TableCell>
            <TableCell>{entry.payment_reference ?? entry.invoice_number}</TableCell>
            <TableCell>
              {entry.type === "OVER_ALLOCATED_PAYMENT"
                ? `Amount ${entry.amount}, allocated ${entry.total_allocated} (over by ${entry.difference})`
                : `Recorded ${entry.recorded_amount_paid}, actual ${entry.actual_allocated_total}`}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
