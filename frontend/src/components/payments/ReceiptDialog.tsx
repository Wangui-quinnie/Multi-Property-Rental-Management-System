import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { PageLoader } from "@/components/shared/PageLoader";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useReceipt } from "@/hooks/usePayments";
import { useDownloadReceiptPdf } from "@/hooks/usePayments";

interface ReceiptDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  paymentId: string;
}

export function ReceiptDialog({ open, onOpenChange, paymentId }: ReceiptDialogProps) {
  const { data: receipt, isLoading } = useReceipt(open ? paymentId : undefined);
  const downloadReceiptPdf = useDownloadReceiptPdf();

  async function handleDownload() {
    if (!receipt) return;
    try {
      await downloadReceiptPdf.mutateAsync({
        paymentId,
        filename: `receipt_${receipt.payment_reference}.pdf`,
      });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Receipt {receipt?.receipt_number}</DialogTitle>
        </DialogHeader>

        {isLoading && <PageLoader />}

        {receipt && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <p className="text-muted-foreground">Tenant</p>
              <p>{receipt.tenant_name} ({receipt.tenant_email})</p>
              <p className="text-muted-foreground">Reference</p>
              <p>{receipt.payment_reference}</p>
              <p className="text-muted-foreground">Method</p>
              <p>{receipt.payment_method}</p>
              <p className="text-muted-foreground">Date</p>
              <p>{receipt.payment_date}</p>
              <p className="text-muted-foreground">Amount paid</p>
              <p>{receipt.amount_paid}</p>
              <p className="text-muted-foreground">Unallocated</p>
              <p>{receipt.unallocated_amount}</p>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice</TableHead>
                  <TableHead>Unit</TableHead>
                  <TableHead>Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {receipt.allocations.map((line) => (
                  <TableRow key={line.invoice_number}>
                    <TableCell>{line.invoice_number}</TableCell>
                    <TableCell>{line.property_name} - {line.unit_number}</TableCell>
                    <TableCell>{line.amount_allocated}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <Button
              variant="outline"
              disabled={downloadReceiptPdf.isPending}
              onClick={handleDownload}
            >
              {downloadReceiptPdf.isPending ? "Downloading..." : "Download PDF"}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
