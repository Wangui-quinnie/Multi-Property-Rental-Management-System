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
import type { Property } from "@/api/properties";

interface PropertyTableProps {
  properties: Property[];
  isLoading: boolean;
  showArchived: boolean;
  onArchive: (property: Property) => void;
  onRestore: (property: Property) => void;
  restoringId?: string;
}

export function PropertyTable({
  properties,
  isLoading,
  showArchived,
  onArchive,
  onRestore,
  restoringId,
}: PropertyTableProps) {
  if (isLoading) {
    return <TableSkeleton columns={6} />;
  }

  if (properties.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        {showArchived ? "No archived properties." : "No properties yet."}
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Location</TableHead>
          <TableHead>Landlord</TableHead>
          <TableHead>Units</TableHead>
          <TableHead>Occupancy</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {properties.map((property) => (
          <TableRow key={property.id}>
            <TableCell>
              <Link to={`/properties/${property.id}`} className="font-medium text-primary hover:underline">
                {property.name}
              </Link>
              <div className="text-xs text-muted-foreground">{property.code}</div>
            </TableCell>
            <TableCell>{property.location}</TableCell>
            <TableCell>{property.landlord_name}</TableCell>
            <TableCell>
              {property.occupied_units}/{property.total_units}
            </TableCell>
            <TableCell>{property.occupancy_rate}%</TableCell>
            <TableCell>{property.status}</TableCell>
            <TableCell className="text-right">
              {showArchived ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRestore(property)}
                  disabled={restoringId === property.id}
                >
                  {restoringId === property.id ? "Restoring..." : "Restore"}
                </Button>
              ) : (
                <Button variant="outline" size="sm" onClick={() => onArchive(property)}>
                  Archive
                </Button>
              )}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}