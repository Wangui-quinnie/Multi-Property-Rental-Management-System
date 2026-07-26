import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageLoader } from "@/components/shared/PageLoader";
import { LeaseForm } from "@/components/leases/LeaseForm";
import { useLease, useUpdateLease } from "@/hooks/useLeases";
import { toast } from "@/components/ui/toast";
import type { LeaseCreate, LeaseUpdate } from "@/api/leases";

export function LeaseEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: lease, isLoading } = useLease(id);
  const updateLease = useUpdateLease(id ?? "");

  async function handleSubmit(data: LeaseCreate | LeaseUpdate) {
    await updateLease.mutateAsync(data as LeaseUpdate);
    toast.add({ title: "Lease updated.", type: "success" });
    navigate("/leases");
  }

  if (isLoading) return <PageLoader />;
  if (!lease) return <p className="text-muted-foreground">Lease not found.</p>;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">
        Edit lease - {lease.tenant_name}
      </h1>
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <LeaseForm
            lease={lease}
            onSubmit={handleSubmit}
            isSubmitting={updateLease.isPending}
            submitError={updateLease.error}
          />
        </CardContent>
      </Card>
    </div>
  );
}