import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { FormField } from "./FormField";

describe("FormField", () => {
  it("associates the label with the control via htmlFor", () => {
    render(
      <FormField label="Email" htmlFor="email">
        <input id="email" />
      </FormField>
    );

    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });

  it("shows a required marker when required", () => {
    const { container } = render(
      <FormField label="Email" htmlFor="email" required>
        <input id="email" />
      </FormField>
    );

    const label = container.querySelector("label");
    expect(label?.textContent).toMatch(/email/i);
    expect(label?.textContent).toContain("*");
  });

  it("renders an error message tied to the field via id", () => {
    render(
      <FormField label="Email" htmlFor="email" error="Required field">
        <input id="email" />
      </FormField>
    );

    const error = screen.getByText("Required field");
    expect(error).toHaveAttribute("id", "email-error");
  });

  it("renders no error message when none is given", () => {
    render(
      <FormField label="Email" htmlFor="email">
        <input id="email" />
      </FormField>
    );

    expect(screen.queryByText(/required field/i)).not.toBeInTheDocument();
  });
});
