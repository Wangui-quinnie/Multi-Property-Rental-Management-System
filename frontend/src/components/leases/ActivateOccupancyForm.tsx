import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { getErrorMessage } from "@/api/errors";
import { useActivateOccupancy } from "@/hooks/useOccupancy";
import { toast } from "@/components/ui/toast";

interface ActivateOccupancyFormProps {
  leaseId: string;
  onSuccess: () => void;
}

// move_in_date defaults to today on the backend if omitted - see
// OccupancyActivateSerializer.
export function ActivateOccupancyForm({ leaseId, onSuccess }: ActivateOccupancyFormProps) {
  const [moveInDate, setMoveInDate] = useState("");
  const activateOccupancy = useActivateOccupancy();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await activateOccupancy.mutateAsync({
      lease: leaseId,
      move_in_date: moveInDate || undefined,
    });
    toast.add({ title: "Occupancy activated.", type: "success" });
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <h3 className="font-medium">Activate occupancy</h3>
      {getErrorMessage(activateOccupancy.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(activateOccupancy.error)}</AlertDescription>
        </Alert>
      )}
      <FormInput
        label="Move-in date"
        id="move_in_date"
        type="date"
        value={moveInDate}
        onChange={(e) => setMoveInDate(e.target.value)}
      />
      <p className="text-xs text-muted-foreground">Leave blank to use today&apos;s date.</p>
      <Button type="submit" disabled={activateOccupancy.isPending}>
        {activateOccupancy.isPending ? "Activating..." : "Activate occupancy"}
      </Button>
    </form>
  );
}