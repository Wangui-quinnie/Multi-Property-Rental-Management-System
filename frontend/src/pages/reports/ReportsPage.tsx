import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/shared/StatCard";
import { PageLoader } from "@/components/shared/PageLoader";
import { FormInput } from "@/components/shared/FormInput";
import { RentReportCard } from "@/components/reports/RentReportCard";
import { WaterReportCard } from "@/components/reports/WaterReportCard";
import { CashFlowSection } from "@/components/reports/CashFlowSection";
import { useLandlordSummary } from "@/hooks/useReports";
import type { ReportDateRangeParams } from "@/api/reports";

/**
 * One dashboard, not tabs like Billing/Payments - there's no CRUD or
 * permission split here, just read-only reporting. Most of the page is
 * driven by the single Landlord Summary endpoint (occupancy/vacancy/
 * arrears/rent/water), which composes the exact same selectors that
 * power their own dedicated dashboards elsewhere, so these numbers can
 * never drift from what's shown on the Properties/Vacancy/Billing pages.
 * Cash flow is the one exception - it gets its own interactive section
 * (see CashFlowSection) since Landlord Summary's embedded version is
 * locked to a 6-month window.
 */
export function ReportsPage() {
  const [appliedRange, setAppliedRange] = useState<ReportDateRangeParams>({});
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { data: summary, isLoading } = useLandlordSummary(appliedRange);

  function handleApplyRange(e: FormEvent) {
    e.preventDefault();
    setAppliedRange({
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    });
  }

  function handleClearRange() {
    setStartDate("");
    setEndDate("");
    setAppliedRange({});
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Reports</h1>

      <form onSubmit={handleApplyRange} className="flex flex-wrap items-end gap-3">
        <FormInput
          label="From"
          id="report_start_date"
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
        <FormInput
          label="To"
          id="report_end_date"
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />
        <Button type="submit">Apply range</Button>
        <Button type="button" variant="outline" onClick={handleClearRange}>
          Clear
        </Button>
      </form>

      {isLoading && <PageLoader />}

      {summary && (
        <>
          <div className="space-y-2">
            <h2 className="text-lg font-medium">Portfolio</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard label="Properties" value={summary.occupancy.total_properties} />
              <StatCard label="Units" value={summary.occupancy.total_units} />
              <StatCard label="Occupancy rate" value={`${summary.occupancy.occupancy_rate}%`} />
              <StatCard label="Potential monthly rent" value={summary.occupancy.potential_monthly_rent} />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-lg font-medium">Vacancy</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard label="Currently vacant units" value={summary.vacancy.currently_vacant_units} />
              <StatCard
                label="Average vacancy duration"
                value={`${summary.vacancy.average_vacancy_duration_days} days`}
              />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-lg font-medium">Arrears</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard label="Portfolio arrears" value={summary.arrears.portfolio_total_arrears} />
              <StatCard label="Leases in arrears" value={summary.arrears.leases_in_arrears} />
              <StatCard label="Tenants in arrears" value={summary.arrears.tenants_in_arrears} />
            </div>
          </div>

          <RentReportCard report={summary.rent} />
          <WaterReportCard report={summary.water} />
        </>
      )}

      <CashFlowSection />
    </div>
  );
}
