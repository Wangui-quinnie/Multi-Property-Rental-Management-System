import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import { NotFound } from "./NotFound";

describe("NotFound", () => {
  it("renders a 404 message and a link back home", () => {
    render(
      <BrowserRouter>
        <NotFound />
      </BrowserRouter>
    );

    expect(screen.getByText("404")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /page not found/i })).toBeInTheDocument();

    const homeLink = screen.getByRole("button", { name: /back to home/i });
    expect(homeLink).toHaveAttribute("href", "/");
  });
});
