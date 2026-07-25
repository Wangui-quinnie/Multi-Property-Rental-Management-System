import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TenantEditForm } from "@/components/tenants/TenantEditForm";
import { useUpdateTenant } from "@/hooks/useTenants";
import { toast } from "@/components/ui/toast";
import type { Tenant, TenantUpdate } from "@/api/tenants";

interface TenantEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tenant: Tenant;
}

export function TenantEditDialog({ open, onOpenChange, tenant }: TenantEditDialogProps) {
  const updateTenant = useUpdateTenant(tenant.id);

  async function handleSubmit(data: TenantUpdate) {
    await updateTenant.mutateAsync(data);
    toast.add({ title: "Tenant updated.", type: "success" });
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit tenant</DialogTitle>
        </DialogHeader>
        <TenantEditForm
          tenant={tenant}
          onSubmit={handleSubmit}
          isSubmitting={updateTenant.isPending}
          submitError={updateTenant.error}
        />
      </DialogContent>
    </Dialog>
  );
}