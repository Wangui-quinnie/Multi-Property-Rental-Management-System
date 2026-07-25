import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TenantCreateForm } from "@/components/tenants/TenantCreateForm";
import { useCreateTenant } from "@/hooks/useTenants";
import { toast } from "@/components/ui/toast";
import type { TenantCreatePayload } from "@/api/tenants";

export function TenantCreatePage() {
  const navigate = useNavigate();
  const createTenant = useCreateTenant();

  async function handleSubmit(data: TenantCreatePayload) {
    await createTenant.mutateAsync(data);
    toast.add({ title: "Tenant created.", type: "success" });
    navigate("/tenants");
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">New tenant</h1>
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <TenantCreateForm
            onSubmit={handleSubmit}
            isSubmitting={createTenant.isPending}
            submitError={createTenant.error}
          />
        </CardContent>
      </Card>
    </div>
  );
}