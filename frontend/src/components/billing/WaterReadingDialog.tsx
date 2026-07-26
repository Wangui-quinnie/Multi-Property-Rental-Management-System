import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { WaterReadingForm } from "@/components/billing/WaterReadingForm";
import { useCreateWaterReading, useUpdateWaterReading } from "@/hooks/useWaterReadings";
import { toast } from "@/components/ui/toast";
import type {
  WaterMeterReading, WaterMeterReadingCreate, WaterMeterReadingUpdate,
} from "@/api/waterReadings";

interface WaterReadingDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Present when editing an existing reading; absent when creating. */
  reading?: WaterMeterReading;
}

export function WaterReadingDialog({ open, onOpenChange, reading }: WaterReadingDialogProps) {
  const createWaterReading = useCreateWaterReading();
  const updateWaterReading = useUpdateWaterReading(reading?.id ?? "");

  const mutation = reading ? updateWaterReading : createWaterReading;

  async function handleSubmit(data: WaterMeterReadingCreate | WaterMeterReadingUpdate) {
    if (reading) {
      await updateWaterReading.mutateAsync(data as WaterMeterReadingUpdate);
    } else {
      await createWaterReading.mutateAsync(data as WaterMeterReadingCreate);
    }
    toast.add({ title: reading ? "Water reading updated." : "Water reading added.", type: "success" });
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{reading ? "Edit water reading" : "Add water reading"}</DialogTitle>
        </DialogHeader>
        <WaterReadingForm
          reading={reading}
          onSubmit={handleSubmit}
          isSubmitting={mutation.isPending}
          submitError={mutation.error}
        />
      </DialogContent>
    </Dialog>
  );
}
