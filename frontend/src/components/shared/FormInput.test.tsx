import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { FormInput } from "./FormInput";

describe("FormInput", () => {
  it("renders a labeled input and forwards value/onChange", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<FormInput label="Email" id="email" value="" onChange={onChange} />);

    const input = screen.getByLabelText("Email");
    await user.type(input, "a");

    expect(onChange).toHaveBeenCalled();
  });

  it("falls back to name for the id when id is omitted", () => {
    render(<FormInput label="Email" name="email" value="" onChange={() => {}} />);

    const input = screen.getByLabelText("Email");
    expect(input).toHaveAttribute("id", "email");
    expect(input).toHaveAttribute("name", "email");
  });

  it("marks the input aria-invalid and links the error message when error is set", () => {
    render(
      <FormInput label="Email" id="email" value="" onChange={() => {}} error="Required" />
    );

    const input = screen.getByLabelText("Email");
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(input).toHaveAttribute("aria-describedby", "email-error");
    expect(screen.getByText("Required")).toBeInTheDocument();
  });

  it("does not mark aria-invalid when there is no error", () => {
    render(<FormInput label="Email" id="email" value="" onChange={() => {}} />);

    const input = screen.getByLabelText("Email");
    expect(input).toHaveAttribute("aria-invalid", "false");
  });
});
