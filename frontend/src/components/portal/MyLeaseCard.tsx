import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOccupancyForLease } from "@/hooks/useOccupancy";
import type { Lease } from "@/api/leases";

interface MyLeaseCardProps {
  lease: Lease;
}

// Read-only - a Tenant's own lease is view-only end to end
// (IsAdminOrLandlordWriteTenantReadOnly), no edit/renew/terminate
// actions here - those stay Admin/Landlord operations.
export function MyLeaseCard({ lease }: MyLeaseCardProps) {
  const { data: occupancy } = useOccupancyForLease(lease.id);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{lease.property_name} - {lease.unit_number}</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-2 text-sm">
        <p className="text-muted-foreground">Status</p>
        <p>{lease.status}</p>
        <p className="text-muted-foreground">Lease start date</p>
        <p>{lease.lease_start_date}</p>
        <p className="text-muted-foreground">Lease end date</p>
        <p>{lease.lease_end_date ?? "-"}</p>
        <p className="text-muted-foreground">Rent amount</p>
        <p>{lease.rent_amount}</p>
        <p className="text-muted-foreground">Deposit amount</p>
        <p>{lease.deposit_amount}</p>
        <p className="text-muted-foreground">Billing day</p>
        <p>{lease.billing_day}</p>
        {occupancy && (
          <>
            <p className="text-muted-foreground">Move-in date</p>
            <p>{occupancy.move_in_date}</p>
          </>
        )}
      </CardContent>
    </Card>
  );
}
