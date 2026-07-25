import { render } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { TableSkeleton } from "./TableSkeleton";

describe("TableSkeleton", () => {
  it("renders the default 5 rows x 4 columns", () => {
    const { container } = render(<TableSkeleton />);

    expect(container.querySelectorAll("thead th").length).toBe(4);
    expect(container.querySelectorAll("tbody tr").length).toBe(5);
    expect(container.querySelectorAll("tbody td").length).toBe(20);
  });

  it("respects custom rows/columns", () => {
    const { container } = render(<TableSkeleton rows={2} columns={3} />);

    expect(container.querySelectorAll("thead th").length).toBe(3);
    expect(container.querySelectorAll("tbody tr").length).toBe(2);
    expect(container.querySelectorAll("tbody td").length).toBe(6);
  });
});
