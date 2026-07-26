import { StatCard } from "@/components/shared/StatCard";
import type { WaterReport } from "@/api/reports";

interface WaterReportCardProps {
  report: WaterReport;
}

export function WaterReportCard({ report }: WaterReportCardProps) {
  return (
    <div className="space-y-2">
      <h2 className="text-lg font-medium">Water</h2>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Units consumed" value={report.total_units_consumed} />
        <StatCard label="Total water billed" value={report.total_water_billed} />
        <StatCard label="Readings" value={report.reading_count} />
      </div>
    </div>
  );
}
