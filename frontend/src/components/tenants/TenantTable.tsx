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
import type { Tenant } from "@/api/tenants";

interface TenantTableProps {
  tenants: Tenant[];
  isLoading: boolean;
  onEdit: (tenant: Tenant) => void;
}

export function TenantTable({ tenants, isLoading, onEdit }: TenantTableProps) {
  if (isLoading) {
    return <TableSkeleton columns={5} />;
  }

  if (tenants.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No tenants yet.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Phone</TableHead>
          <TableHead>National ID</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {tenants.map((tenant) => (
          <TableRow key={tenant.id}>
            <TableCell className="font-medium">{tenant.full_name || "—"}</TableCell>
            <TableCell>{tenant.email}</TableCell>
            <TableCell>{tenant.phone_number || "—"}</TableCell>
            <TableCell>{tenant.national_id || "—"}</TableCell>
            <TableCell>{tenant.status}</TableCell>
            <TableCell className="text-right">
              <Button variant="outline" size="sm" onClick={() => onEdit(tenant)}>
                Edit
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}