import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ActivateOccupancyForm } from "@/components/leases/ActivateOccupancyForm";
import { LeaseRenewForm } from "@/components/leases/LeaseRenewForm";
import { LeaseTerminateForm } from "@/components/leases/LeaseTerminateForm";
import { useOccupancyForLease } from "@/hooks/useOccupancy";
import type { Lease } from "@/api/leases";

interface LeaseActionsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  lease: Lease;
}

/**
 * Renew/Terminate/Activate live here as actions on the Lease, not
 * separate pages (per the project roadmap). Renew and Terminate are
 * both always offered for an ACTIVE lease regardless of Occupancy
 * state - the backend only rejects Renew if this lease has already
 * been renewed once (LeaseSerializer doesn't expose that flag, so we
 * can't hide the button preemptively; the error surfaces inline if so).
 * Activate is hidden once an Occupancy already exists for this lease.
 */
export function LeaseActionsDialog({ open, onOpenChange, lease }: LeaseActionsDialogProps) {
  const { data: occupancy, isLoading } = useOccupancyForLease(open ? lease.id : undefined);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            Manage lease - {lease.tenant_name} ({lease.property_name} - {lease.unit_number})
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {!isLoading && !occupancy && (
            <ActivateOccupancyForm leaseId={lease.id} onSuccess={() => onOpenChange(false)} />
          )}

          {occupancy && (
            <p className="text-sm text-muted-foreground">
              Occupancy active since {occupancy.move_in_date}.
            </p>
          )}

          <LeaseRenewForm lease={lease} onSuccess={() => onOpenChange(false)} />

          <LeaseTerminateForm leaseId={lease.id} onSuccess={() => onOpenChange(false)} />
        </div>
      </DialogContent>
    </Dialog>
  );
}