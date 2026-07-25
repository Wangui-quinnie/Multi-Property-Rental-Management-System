import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import { Landing } from "./Landing";

describe("Landing", () => {
  it("renders the hero heading and a sign-in link", () => {
    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );

    expect(
      screen.getByRole("heading", { name: /manage your rental properties/i })
    ).toBeInTheDocument();

    const ctaButtons = screen.getAllByRole("button", { name: /sign in|get started/i });
    expect(ctaButtons.length).toBeGreaterThan(0);
    ctaButtons.forEach((button) => {
      expect(button).toHaveAttribute("href", "/login");
    });
  });
});