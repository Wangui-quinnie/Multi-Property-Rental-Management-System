import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useGenerateRentInvoices } from "@/hooks/useInvoices";
import type { BillingPeriod } from "@/api/billingPeriods";

interface BillingPeriodTableProps {
  periods: BillingPeriod[];
  isLoading: boolean;
  /** Only Admin can create/edit periods (BillingPeriodViewSet's
   * IsAdminWriteAuthenticatedReadOnly) - Landlord gets a read-only row. */
  canWrite: boolean;
  onEdit: (period: BillingPeriod) => void;
  onApplyLateFees: (period: BillingPeriod) => void;
}

export function BillingPeriodTable({
  periods,
  isLoading,
  canWrite,
  onEdit,
  onApplyLateFees,
}: BillingPeriodTableProps) {
  const generateRentInvoices = useGenerateRentInvoices();

  if (isLoading) return <TableSkeleton columns={6} />;
  if (periods.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No billing periods yet.</p>;
  }

  async function handleGenerateRent(period: BillingPeriod) {
    try {
      const invoices = await generateRentInvoices.mutateAsync({ billing_period: period.id });
      toast.add({
        title: `Generated or refreshed ${invoices.length} invoice(s) for ${period.name}.`,
        type: "success",
      });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Start date</TableHead>
          <TableHead>End date</TableHead>
          <TableHead>Due date</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {periods.map((period) => (
          <TableRow key={period.id}>
            <TableCell className="font-medium">{period.name}</TableCell>
            <TableCell>{period.start_date}</TableCell>
            <TableCell>{period.end_date}</TableCell>
            <TableCell>{period.due_date}</TableCell>
            <TableCell>{period.status}</TableCell>
            <TableCell className="text-right space-x-2">
              {canWrite && (
                <Button variant="outline" size="sm" onClick={() => onEdit(period)}>
                  Edit
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                disabled={period.status !== "OPEN" || generateRentInvoices.isPending}
                onClick={() => handleGenerateRent(period)}
              >
                Generate rent invoices
              </Button>
              <Button variant="outline" size="sm" onClick={() => onApplyLateFees(period)}>
                Apply late fees
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
