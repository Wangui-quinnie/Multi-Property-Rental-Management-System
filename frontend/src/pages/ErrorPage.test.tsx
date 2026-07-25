import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, afterEach } from "vitest";
import { ErrorPage } from "./ErrorPage";

describe("ErrorPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders an error message and a reload button", () => {
    render(<ErrorPage />);

    expect(screen.getByRole("heading", { name: /an unexpected error occurred/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /reload/i })).toBeInTheDocument();
  });

  it("calls onReset when the reload button is clicked", async () => {
    // jsdom doesn't implement real navigation; stub it so clicking Reload
    // doesn't spam "Not implemented" console noise.
    // @ts-expect-error - jsdom location is not fully implemented
    delete window.location;
    window.location = { href: "" } as Location;

    const onReset = vi.fn();
    const user = userEvent.setup();

    render(<ErrorPage onReset={onReset} />);
    await user.click(screen.getByRole("button", { name: /reload/i }));

    expect(onReset).toHaveBeenCalledTimes(1);
  });
});
