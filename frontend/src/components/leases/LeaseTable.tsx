import { Link } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { Lease } from "@/api/leases";

interface LeaseTableProps {
  leases: Lease[];
  isLoading: boolean;
  onManage: (lease: Lease) => void;
}

export function LeaseTable({ leases, isLoading, onManage }: LeaseTableProps) {
  if (isLoading) {
    return <TableSkeleton columns={6} />;
  }

  if (leases.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No leases yet.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Tenant</TableHead>
          <TableHead>Unit</TableHead>
          <TableHead>Rent</TableHead>
          <TableHead>Start date</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {leases.map((lease) => (
          <TableRow key={lease.id}>
            <TableCell className="font-medium">{lease.tenant_name}</TableCell>
            <TableCell>
              {lease.property_name} - {lease.unit_number}
            </TableCell>
            <TableCell>{lease.rent_amount}</TableCell>
            <TableCell>{lease.lease_start_date}</TableCell>
            <TableCell>{lease.status}</TableCell>
            <TableCell className="text-right space-x-2">
              {lease.status === "ACTIVE" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    render={<Link to={`/leases/${lease.id}/edit`} />}
                    nativeButton={false}
                  >
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => onManage(lease)}>
                    Manage
                  </Button>
                </>
              )}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}