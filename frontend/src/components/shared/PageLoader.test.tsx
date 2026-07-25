import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PageLoader } from "./PageLoader";

describe("PageLoader", () => {
  it("renders without a label paragraph by default", () => {
    const { container } = render(<PageLoader />);
    expect(container.querySelector("p")).not.toBeInTheDocument();
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("renders an optional label", () => {
    render(<PageLoader label="Loading properties..." />);
    expect(screen.getByText("Loading properties...")).toBeInTheDocument();
  });

  it("applies the min-h-screen class when fullScreen is set", () => {
    const { container } = render(<PageLoader fullScreen />);
    expect(container.firstChild).toHaveClass("min-h-screen");
  });

  it("does not apply min-h-screen by default", () => {
    const { container } = render(<PageLoader />);
    expect(container.firstChild).not.toHaveClass("min-h-screen");
  });
});
