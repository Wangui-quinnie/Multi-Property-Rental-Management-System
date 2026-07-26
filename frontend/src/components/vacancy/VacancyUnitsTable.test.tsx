import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { VacancyUnitsTable } from "./VacancyUnitsTable";

describe("VacancyUnitsTable", () => {
  it("renders a row per vacant unit", () => {
    render(
      <VacancyUnitsTable
        isLoading={false}
        vacantUnits={[
          { unit_id: "unit-1", unit_number: "A1", vacated_at: "2026-01-01", days_vacant: 10 },
        ]}
      />
    );

    expect(screen.getByText("A1")).toBeInTheDocument();
    expect(screen.getByText("2026-01-01")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
  });

  it("shows an empty-state message when there are no vacant units", () => {
    render(<VacancyUnitsTable isLoading={false} vacantUnits={[]} />);
    expect(screen.getByText("No vacant units right now.")).toBeInTheDocument();
  });
});