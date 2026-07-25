import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { FormSelect } from "./FormSelect";

describe("FormSelect", () => {
  it("renders a labeled select with its options", () => {
    render(
      <FormSelect label="Status" id="status" value="ACTIVE" onChange={() => {}}>
        <option value="ACTIVE">Active</option>
        <option value="INACTIVE">Inactive</option>
      </FormSelect>
    );

    const select = screen.getByLabelText("Status") as HTMLSelectElement;
    expect(select).toBeInTheDocument();
    expect(select.value).toBe("ACTIVE");
  });

  it("calls onChange when a different option is selected", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <FormSelect label="Status" id="status" value="ACTIVE" onChange={onChange}>
        <option value="ACTIVE">Active</option>
        <option value="INACTIVE">Inactive</option>
      </FormSelect>
    );

    await user.selectOptions(screen.getByLabelText("Status"), "INACTIVE");
    expect(onChange).toHaveBeenCalled();
  });

  it("marks aria-invalid and shows the error message when error is set", () => {
    render(
      <FormSelect label="Status" id="status" value="ACTIVE" onChange={() => {}} error="Required">
        <option value="ACTIVE">Active</option>
      </FormSelect>
    );

    const select = screen.getByLabelText("Status");
    expect(select).toHaveAttribute("aria-invalid", "true");
    expect(select).toHaveAttribute("aria-describedby", "status-error");
    expect(screen.getByText("Required")).toBeInTheDocument();
  });

  it("throws if neither id nor name is provided", () => {
    // Both `id` and `name` are optional in FormSelectProps (mirroring the
    // underlying <select>), so omitting both is not a type error — the
    // guard is a runtime check (see FormSelect.tsx), so no ts-expect-error
    // is needed here.
    expect(() =>
      render(
        <FormSelect label="Status" value="ACTIVE" onChange={() => {}}>
          <option value="ACTIVE">Active</option>
        </FormSelect>
      )
    ).toThrow();
  });
});