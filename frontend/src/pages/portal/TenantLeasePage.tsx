import { MyLeaseCard } from "@/components/portal/MyLeaseCard";
import { PageLoader } from "@/components/shared/PageLoader";
import { useLeases } from "@/hooks/useLeases";

// get_leases_for_user() scopes this list server-side to the logged-in
// Tenant's own lease(s) (tenant__user=user) - no client-side filtering
// needed, and no params/filters exposed since a Tenant has nothing to
// filter by.
export function TenantLeasePage() {
  const { data: leasesPage, isLoading } = useLeases();
  const leases = leasesPage?.results ?? [];

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">My Lease</h1>

      {leases.length === 0 && (
        <p className="text-sm text-muted-foreground">No lease on record.</p>
      )}

      <div className="space-y-4">
        {leases.map((lease) => (
          <MyLeaseCard key={lease.id} lease={lease} />
        ))}
      </div>
    </div>
  );
}
