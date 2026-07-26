import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { CashFlowSection } from "./CashFlowSection";
import { useCashFlowTrend } from "@/hooks/useReports";

vi.mock("@/hooks/useReports");

const mockedUseCashFlowTrend = vi.mocked(useCashFlowTrend);

describe("CashFlowSection", () => {
  beforeEach(() => {
    mockedUseCashFlowTrend.mockReturnValue({
      data: [{ month: "2026-01", total_collected: "50000.00" }],
      isLoading: false,
    } as never);
  });

  it("renders a row per month and defaults to a 6-month window", () => {
    render(<CashFlowSection />);

    expect(screen.getByText("2026-01")).toBeInTheDocument();
    expect(screen.getByText("50000.00")).toBeInTheDocument();
    expect(mockedUseCashFlowTrend).toHaveBeenCalledWith({ months: 6 });
  });

  it("refetches with the selected months window when changed", async () => {
    const user = userEvent.setup();
    render(<CashFlowSection />);

    await user.click(screen.getByRole("button", { name: /12 months/i }));

    expect(mockedUseCashFlowTrend).toHaveBeenLastCalledWith({ months: 12 });
  });

  it("shows an empty-state message when there are no confirmed payments", () => {
    mockedUseCashFlowTrend.mockReturnValue({ data: [], isLoading: false } as never);
    render(<CashFlowSection />);
    expect(screen.getByText("No confirmed payments yet.")).toBeInTheDocument();
  });
});
