import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormInput } from "@/components/shared/FormInput";
import { getErrorMessage } from "@/api/errors";
import { useTerminateLease } from "@/hooks/useLeases";
import { toast } from "@/components/ui/toast";

interface LeaseTerminateFormProps {
  leaseId: string;
  onSuccess: () => void;
}

// termination_date defaults to today on the backend if omitted - see
// LeaseTerminateSerializer. This also ends any active Occupancy, frees
// the Unit, and opens a VacancyPeriod (see terminate_lease()).
export function LeaseTerminateForm({ leaseId, onSuccess }: LeaseTerminateFormProps) {
  const [terminationDate, setTerminationDate] = useState("");
  const terminateLease = useTerminateLease(leaseId);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await terminateLease.mutateAsync({ termination_date: terminationDate || undefined });
    toast.add({ title: "Lease terminated.", type: "success" });
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <h3 className="font-medium">Terminate lease</h3>
      {getErrorMessage(terminateLease.error, "") && (
        <Alert variant="destructive">
          <AlertDescription>{getErrorMessage(terminateLease.error)}</AlertDescription>
        </Alert>
      )}
      <FormInput
        label="Termination date"
        id="termination_date"
        type="date"
        value={terminationDate}
        onChange={(e) => setTerminationDate(e.target.value)}
      />
      <p className="text-xs text-muted-foreground">
        Leave blank to use today&apos;s date. This frees the unit and ends any active occupancy.
      </p>
      <Button type="submit" variant="destructive" disabled={terminateLease.isPending}>
        {terminateLease.isPending ? "Terminating..." : "Terminate lease"}
      </Button>
    </form>
  );
}