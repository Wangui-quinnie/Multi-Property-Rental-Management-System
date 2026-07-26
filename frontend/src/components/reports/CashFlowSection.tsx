import { useState } from "react";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/shared/TableSkeleton";
import { useCashFlowTrend } from "@/hooks/useReports";

const MONTH_OPTIONS = [3, 6, 12] as const;

/**
 * Has its own months selector rather than relying on Landlord Summary's
 * embedded cash_flow section, which always calls get_cash_flow_trend()
 * with the default months=6 (see apps/reports/selectors/reports.py) -
 * this hits the dedicated /reports/cash-flow/ endpoint directly so the
 * range can actually be changed.
 */
export function CashFlowSection() {
  const [months, setMonths] = useState<(typeof MONTH_OPTIONS)[number]>(6);
  const { data: entries, isLoading } = useCashFlowTrend({ months });

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">Cash flow trend</h2>
        <div className="flex gap-2">
          {MONTH_OPTIONS.map((option) => (
            <Button
              key={option}
              variant={months === option ? "secondary" : "outline"}
              size="sm"
              onClick={() => setMonths(option)}
            >
              {option} months
            </Button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <TableSkeleton columns={2} />
      ) : !entries || entries.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">No confirmed payments yet.</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Month</TableHead>
              <TableHead>Total collected</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {entries.map((entry) => (
              <TableRow key={entry.month}>
                <TableCell className="font-medium">{entry.month}</TableCell>
                <TableCell>{entry.total_collected}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
