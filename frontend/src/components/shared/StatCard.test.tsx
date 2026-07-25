import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StatCard } from "./StatCard";

describe("StatCard", () => {
  it("renders the label and value", () => {
    render(<StatCard label="Properties" value={12} />);
    expect(screen.getByText("Properties")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("renders an optional hint", () => {
    render(<StatCard label="Occupancy" value="80%" hint="Across all active units" />);
    expect(screen.getByText("Across all active units")).toBeInTheDocument();
  });

  it("omits the hint paragraph when none is given", () => {
    const { container } = render(<StatCard label="Units" value={4} />);
    expect(container.querySelectorAll("p").length).toBe(0);
  });
});