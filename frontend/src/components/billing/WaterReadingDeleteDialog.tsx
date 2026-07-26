import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface WaterReadingDeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  unitLabel: string;
  onConfirm: () => void;
  isPending?: boolean;
}

/**
 * Unlike Property/Unit's "archive" (soft-delete), this is a real DELETE -
 * WaterMeterReading has no archival mixin. The backend already refuses
 * (400) to delete a reading that's been billed (has an invoice_item), so
 * this dialog is only ever reachable for unbilled readings.
 */
export function WaterReadingDeleteDialog({
  open,
  onOpenChange,
  unitLabel,
  onConfirm,
  isPending,
}: WaterReadingDeleteDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete this water reading?</AlertDialogTitle>
          <AlertDialogDescription>
            This permanently removes the reading for {unitLabel}. This cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={isPending}>
            {isPending ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
