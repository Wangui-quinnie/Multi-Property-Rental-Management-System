import { StatCard } from "@/components/shared/StatCard";
import { VacancyUnitsTable } from "@/components/vacancy/VacancyUnitsTable";
import { useVacancyDashboard } from "@/hooks/useVacancy";

export function VacancyPage() {
  const { data: dashboard, isLoading } = useVacancyDashboard();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Vacancy</h1>

      {dashboard && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-2">
          <StatCard label="Currently vacant units" value={dashboard.currently_vacant_units} />
          <StatCard
            label="Average vacancy duration"
            value={`${dashboard.average_vacancy_duration_days} days`}
            hint="Among vacancies that have since been filled"
          />
        </div>
      )}

      <VacancyUnitsTable vacantUnits={dashboard?.vacant_units ?? []} isLoading={isLoading} />
    </div>
  );
}