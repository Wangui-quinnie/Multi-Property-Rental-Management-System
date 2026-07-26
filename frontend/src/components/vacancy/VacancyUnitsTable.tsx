import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import type { VacancyDashboard } from "@/api/vacancy";

interface VacancyUnitsTableProps {
  vacantUnits: VacancyDashboard["vacant_units"];
  isLoading: boolean;
}

export function VacancyUnitsTable({ vacantUnits, isLoading }: VacancyUnitsTableProps) {
  if (isLoading) {
    return <TableSkeleton columns={3} />;
  }

  if (vacantUnits.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No vacant units right now.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Unit</TableHead>
          <TableHead>Vacant since</TableHead>
          <TableHead>Days vacant</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {vacantUnits.map((unit) => (
          <TableRow key={unit.unit_id}>
            <TableCell className="font-medium">{unit.unit_number}</TableCell>
            <TableCell>{unit.vacated_at}</TableCell>
            <TableCell>{unit.days_vacant}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}