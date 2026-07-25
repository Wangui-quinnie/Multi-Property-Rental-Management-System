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
import type { Unit } from "@/api/properties";

interface UnitTableProps {
  units: Unit[];
  isLoading: boolean;
  showArchived: boolean;
  /** Hide the Property column when already scoped to one property (e.g. within a Property detail page). */
  showPropertyColumn?: boolean;
  onEdit: (unit: Unit) => void;
  onArchive: (unit: Unit) => void;
  onRestore: (unit: Unit) => void;
  restoringId?: string;
}

export function UnitTable({
  units,
  isLoading,
  showArchived,
  showPropertyColumn = true,
  onEdit,
  onArchive,
  onRestore,
  restoringId,
}: UnitTableProps) {
  if (isLoading) {
    return <TableSkeleton columns={showPropertyColumn ? 6 : 5} />;
  }

  if (units.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        {showArchived ? "No archived units." : "No units yet."}
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Unit</TableHead>
          {showPropertyColumn && <TableHead>Property</TableHead>}
          <TableHead>Rent</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {units.map((unit) => (
          <TableRow key={unit.id}>
            <TableCell>
              <div className="font-medium">{unit.unit_number}</div>
              {unit.unit_type && <div className="text-xs text-muted-foreground">{unit.unit_type}</div>}
            </TableCell>
            {showPropertyColumn && <TableCell>{unit.property_name}</TableCell>}
            <TableCell>{unit.rent_amount}</TableCell>
            <TableCell>{unit.status}</TableCell>
            <TableCell className="text-right space-x-2">
              {showArchived ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRestore(unit)}
                  disabled={restoringId === unit.id}
                >
                  {restoringId === unit.id ? "Restoring..." : "Restore"}
                </Button>
              ) : (
                <>
                  <Button variant="outline" size="sm" onClick={() => onEdit(unit)}>
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => onArchive(unit)}>
                    Archive
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