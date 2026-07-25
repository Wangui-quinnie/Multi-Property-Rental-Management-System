import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { UnitForm } from "@/components/properties/UnitForm";
import { useCreateUnit, useUpdateUnit } from "@/hooks/useUnits";
import { toast } from "@/components/ui/toast";
import type { Unit, UnitCreate, UnitUpdate } from "@/api/properties";

interface UnitFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  propertyId: string;
  /** Present when editing an existing unit; absent when adding a new one. */
  unit?: Unit;
}

export function UnitFormDialog({ open, onOpenChange, propertyId, unit }: UnitFormDialogProps) {
  const isEdit = !!unit;
  const createUnit = useCreateUnit();
  const updateUnit = useUpdateUnit(unit?.id ?? "");

  // Kept as two explicit branches rather than a single shared
  // `mutation` variable — a union of the two mutation result types
  // makes `.mutateAsync`'s argument type awkward to call safely
  // without a compiler on hand to double check it.
  async function handleSubmit(data: UnitCreate | UnitUpdate) {
    if (isEdit) {
      await updateUnit.mutateAsync(data as UnitUpdate);
    } else {
      await createUnit.mutateAsync(data as UnitCreate);
    }
    toast.add({ title: isEdit ? "Unit updated." : "Unit added.", type: "success" });
    onOpenChange(false);
  }

  const isSubmitting = isEdit ? updateUnit.isPending : createUnit.isPending;
  const submitError = isEdit ? updateUnit.error : createUnit.error;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit unit" : "Add unit"}</DialogTitle>
        </DialogHeader>
        <UnitForm
          propertyId={propertyId}
          unit={unit}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          submitError={submitError}
        />
      </DialogContent>
    </Dialog>
  );
}