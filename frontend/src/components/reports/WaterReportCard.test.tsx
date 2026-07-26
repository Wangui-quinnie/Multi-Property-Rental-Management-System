import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { WaterReportCard } from "./WaterReportCard";
import type { WaterReport } from "@/api/reports";

const sampleReport: WaterReport = {
  total_units_consumed: "500.00",
  total_water_billed: "25000.00",
  reading_count: 20,
};

describe("WaterReportCard", () => {
  it("renders all three figures", () => {
    render(<WaterReportCard report={sampleReport} />);

    expect(screen.getByText("500.00")).toBeInTheDocument();
    expect(screen.getByText("25000.00")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();
  });
});
