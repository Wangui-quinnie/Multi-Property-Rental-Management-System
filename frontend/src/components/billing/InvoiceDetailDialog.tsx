import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { ApplyLateFeeForm } from "@/components/billing/ApplyLateFeeForm";
import type { Invoice } from "@/api/invoices";

interface InvoiceDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  invoice: Invoice;
}

export function InvoiceDetailDialog({ open, onOpenChange, invoice }: InvoiceDetailDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            Invoice {invoice.invoice_number} - {invoice.tenant_name}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <p className="text-muted-foreground">Unit</p>
            <p>{invoice.property_name} - {invoice.unit_number}</p>
            <p className="text-muted-foreground">Billing period</p>
            <p>{invoice.billing_period_name}</p>
            <p className="text-muted-foreground">Due date</p>
            <p>{invoice.due_date}</p>
            <p className="text-muted-foreground">Status</p>
            <p>{invoice.is_overdue ? "OVERDUE" : invoice.status}</p>
            <p className="text-muted-foreground">Balance</p>
            <p>{invoice.balance}</p>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Item</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Qty</TableHead>
                <TableHead>Unit price</TableHead>
                <TableHead>Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoice.items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.item_type}</TableCell>
                  <TableCell>{item.description}</TableCell>
                  <TableCell>{item.quantity}</TableCell>
                  <TableCell>{item.unit_price}</TableCell>
                  <TableCell>{item.amount}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {invoice.is_overdue && (
            <ApplyLateFeeForm invoiceId={invoice.id} onSuccess={() => onOpenChange(false)} />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
