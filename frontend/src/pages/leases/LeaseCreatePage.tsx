import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LeaseForm } from "@/components/leases/LeaseForm";
import { useCreateLease } from "@/hooks/useLeases";
import { toast } from "@/components/ui/toast";
import type { LeaseCreate, LeaseUpdate } from "@/api/leases";

export function LeaseCreatePage() {
  const navigate = useNavigate();
  const createLease = useCreateLease();

  // LeaseForm is shared between create/edit, so its onSubmit prop
  // accepts either shape - this page only ever renders in create mode
  // (no `lease` passed to LeaseForm below), so it's always actually a
  // LeaseCreate at runtime.
  async function handleSubmit(data: LeaseCreate | LeaseUpdate) {
    await createLease.mutateAsync(data as LeaseCreate);
    toast.add({ title: "Lease created.", type: "success" });
    navigate("/leases");
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">New lease</h1>
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <LeaseForm
            onSubmit={handleSubmit}
            isSubmitting={createLease.isPending}
            submitError={createLease.error}
          />
        </CardContent>
      </Card>
    </div>
  );
}