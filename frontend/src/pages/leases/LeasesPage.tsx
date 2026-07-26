import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { LeaseTable } from "@/components/leases/LeaseTable";
import { LeaseActionsDialog } from "@/components/leases/LeaseActionsDialog";
import { useLeases } from "@/hooks/useLeases";
import type { Lease, LeaseListParams } from "@/api/leases";

type StatusFilter = "ALL" | "ACTIVE" | "ENDED" | "CANCELLED";

export function LeasesPage() {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ACTIVE");
  const [managingLease, setManagingLease] = useState<Lease | undefined>();

  const params: LeaseListParams | undefined =
    statusFilter === "ALL" ? undefined : { status: statusFilter };
  const { data: leasesPage, isLoading } = useLeases(params);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Leases</h1>
        <Button render={<Link to="/leases/new" />} nativeButton={false}>
          New lease
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {(["ACTIVE", "ENDED", "CANCELLED", "ALL"] as const).map((status) => (
          <Button
            key={status}
            variant={statusFilter === status ? "secondary" : "outline"}
            size="sm"
            onClick={() => setStatusFilter(status)}
          >
            {status === "ALL" ? "All" : status.charAt(0) + status.slice(1).toLowerCase()}
          </Button>
        ))}
      </div>

      <LeaseTable
        leases={leasesPage?.results ?? []}
        isLoading={isLoading}
        onManage={setManagingLease}
      />

      {managingLease && (
        <LeaseActionsDialog
          open={!!managingLease}
          onOpenChange={(open) => !open && setManagingLease(undefined)}
          lease={managingLease}
        />
      )}
    </div>
  );
}