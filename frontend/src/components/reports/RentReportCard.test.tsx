import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { RentReportCard } from "./RentReportCard";
import type { RentReport } from "@/api/reports";

const sampleReport: RentReport = {
  rent_billed: "150000.00",
  total_billed: "160000.00",
  total_collected: "120000.00",
  total_outstanding: "40000.00",
  invoice_count: 10,
};

describe("RentReportCard", () => {
  it("renders all four figures", () => {
    render(<RentReportCard report={sampleReport} />);

    expect(screen.getByText("150000.00")).toBeInTheDocument();
    expect(screen.getByText("160000.00")).toBeInTheDocument();
    expect(screen.getByText("120000.00")).toBeInTheDocument();
    expect(screen.getByText("40000.00")).toBeInTheDocument();
  });
});
