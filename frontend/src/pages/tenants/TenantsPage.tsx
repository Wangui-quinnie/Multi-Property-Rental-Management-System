import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TenantTable } from "@/components/tenants/TenantTable";
import { TenantEditDialog } from "@/components/tenants/TenantEditDialog";
import { useTenants } from "@/hooks/useTenants";
import type { Tenant } from "@/api/tenants";

export function TenantsPage() {
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [editingTenant, setEditingTenant] = useState<Tenant | undefined>();

  // Debounce so we don't refetch on every keystroke.
  useEffect(() => {
    const timeout = setTimeout(() => setSearch(searchInput), 300);
    return () => clearTimeout(timeout);
  }, [searchInput]);

  const { data: tenantsPage, isLoading } = useTenants(search ? { search } : undefined);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Tenants</h1>
        <Button render={<Link to="/tenants/new" />} nativeButton={false}>
          New tenant
        </Button>
      </div>

      <Input
        placeholder="Search by name, email, or national ID..."
        aria-label="Search tenants"
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
        className="max-w-sm"
      />

      <TenantTable
        tenants={tenantsPage?.results ?? []}
        isLoading={isLoading}
        onEdit={setEditingTenant}
      />

      {editingTenant && (
        <TenantEditDialog
          open={!!editingTenant}
          onOpenChange={(open) => !open && setEditingTenant(undefined)}
          tenant={editingTenant}
        />
      )}
    </div>
  );
}