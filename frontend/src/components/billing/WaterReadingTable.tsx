import { useState } from "react";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import { WaterReadingDeleteDialog } from "@/components/billing/WaterReadingDeleteDialog";
import { getErrorMessage } from "@/api/errors";
import { toast } from "@/components/ui/toast";
import { useApplyWaterCharge, useDeleteWaterReading } from "@/hooks/useWaterReadings";
import type { WaterMeterReading } from "@/api/waterReadings";

interface WaterReadingTableProps {
  readings: WaterMeterReading[];
  isLoading: boolean;
  onEdit: (reading: WaterMeterReading) => void;
}

export function WaterReadingTable({ readings, isLoading, onEdit }: WaterReadingTableProps) {
  const [deletingReading, setDeletingReading] = useState<WaterMeterReading | undefined>();

  const applyWaterCharge = useApplyWaterCharge();
  const deleteWaterReading = useDeleteWaterReading();

  if (isLoading) return <TableSkeleton columns={8} />;
  if (readings.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No water readings yet.</p>;
  }

  async function handleApplyCharge(reading: WaterMeterReading) {
    try {
      await applyWaterCharge.mutateAsync(reading.id);
      toast.add({ title: "Water charge applied to invoice.", type: "success" });
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  async function handleConfirmDelete() {
    if (!deletingReading) return;
    try {
      await deleteWaterReading.mutateAsync(deletingReading.id);
      toast.add({ title: "Water reading deleted.", type: "success" });
      setDeletingReading(undefined);
    } catch (error) {
      toast.add({ title: getErrorMessage(error), type: "error" });
    }
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Unit</TableHead>
            <TableHead>Billing period</TableHead>
            <TableHead>Previous</TableHead>
            <TableHead>Current</TableHead>
            <TableHead>Consumed</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Billed</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {readings.map((reading) => (
            <TableRow key={reading.id}>
              <TableCell className="font-medium">
                {reading.property_name} - {reading.unit_number}
              </TableCell>
              <TableCell>{reading.billing_period_name}</TableCell>
              <TableCell>{reading.previous_reading}</TableCell>
              <TableCell>{reading.current_reading}</TableCell>
              <TableCell>{reading.units_consumed}</TableCell>
              <TableCell>{reading.amount}</TableCell>
              <TableCell>{reading.is_billed ? "Yes" : "No"}</TableCell>
              <TableCell className="text-right space-x-2">
                <Button variant="outline" size="sm" onClick={() => onEdit(reading)}>
                  Edit
                </Button>
                {!reading.is_billed && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={applyWaterCharge.isPending}
                      onClick={() => handleApplyCharge(reading)}
                    >
                      Apply charge
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => setDeletingReading(reading)}>
                      Delete
                    </Button>
                  </>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {deletingReading && (
        <WaterReadingDeleteDialog
          open={!!deletingReading}
          onOpenChange={(open) => !open && setDeletingReading(undefined)}
          unitLabel={`${deletingReading.property_name} - ${deletingReading.unit_number}`}
          onConfirm={handleConfirmDelete}
          isPending={deleteWaterReading.isPending}
        />
      )}
    </>
  );
}
