import { StatCard } from "@/components/shared/StatCard";
import type { RentReport } from "@/api/reports";

interface RentReportCardProps {
  report: RentReport;
}

export function RentReportCard({ report }: RentReportCardProps) {
  return (
    <div className="space-y-2">
      <h2 className="text-lg font-medium">Rent</h2>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Rent billed" value={report.rent_billed} />
        <StatCard label="Total billed" value={report.total_billed} hint="Rent + other charges" />
        <StatCard label="Total collected" value={report.total_collected} />
        <StatCard label="Outstanding" value={report.total_outstanding} />
      </div>
    </div>
  );
}
