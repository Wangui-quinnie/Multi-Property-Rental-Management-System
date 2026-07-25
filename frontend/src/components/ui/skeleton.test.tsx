import { render } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Skeleton } from "./skeleton";

describe("Skeleton", () => {
  it("renders a pulsing placeholder div with a merged className", () => {
    const { container } = render(<Skeleton className="h-4 w-24" data-testid="sk" />);
    const el = container.querySelector('[data-slot="skeleton"]');

    expect(el).toBeInTheDocument();
    expect(el).toHaveClass("animate-pulse", "h-4", "w-24");
  });
});
