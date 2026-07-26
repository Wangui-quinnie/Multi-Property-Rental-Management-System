import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { Invoice } from "@/api/invoices";

interface InvoiceTableProps {
  invoices: Invoice[];
  isLoading: boolean;
  onViewDetail: (invoice: Invoice) => void;
}

export function InvoiceTable({ invoices, isLoading, onViewDetail }: InvoiceTableProps) {
  if (isLoading) return <TableSkeleton columns={7} />;
  if (invoices.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No invoices yet.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Invoice #</TableHead>
          <TableHead>Tenant</TableHead>
          <TableHead>Unit</TableHead>
          <TableHead>Billing period</TableHead>
          <TableHead>Total</TableHead>
          <TableHead>Balance</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {invoices.map((invoice) => (
          <TableRow key={invoice.id}>
            <TableCell className="font-medium">{invoice.invoice_number}</TableCell>
            <TableCell>{invoice.tenant_name}</TableCell>
            <TableCell>{invoice.property_name} - {invoice.unit_number}</TableCell>
            <TableCell>{invoice.billing_period_name}</TableCell>
            <TableCell>{invoice.total_amount}</TableCell>
            <TableCell>{invoice.balance}</TableCell>
            <TableCell>{invoice.is_overdue ? "OVERDUE" : invoice.status}</TableCell>
            <TableCell className="text-right">
              <Button variant="outline" size="sm" onClick={() => onViewDetail(invoice)}>
                View
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
