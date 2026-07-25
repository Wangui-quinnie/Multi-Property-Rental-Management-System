import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError, AxiosHeaders } from "axios";
import { describe, it, expect, vi } from "vitest";
import { TenantCreateForm } from "./TenantCreateForm";

function makeAxiosError(data: unknown) {
  return new AxiosError("Request failed", "ERR_BAD_REQUEST", undefined, undefined, {
    status: 400,
    statusText: "Bad Request",
    headers: {},
    config: { headers: new AxiosHeaders() },
    data,
  });
}

describe("TenantCreateForm", () => {
  it("renders all expected fields", () => {
    render(<TenantCreateForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);

    expect(screen.getByLabelText(/^email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument();
    expect(screen.getByLabelText("First name")).toBeInTheDocument();
    expect(screen.getByLabelText("Last name")).toBeInTheDocument();
    expect(screen.getByLabelText("Phone number")).toBeInTheDocument();
    expect(screen.getByLabelText("National ID")).toBeInTheDocument();
    expect(screen.getByLabelText("Emergency contact name")).toBeInTheDocument();
    expect(screen.getByLabelText("Emergency contact phone")).toBeInTheDocument();
  });

  it("submits the full payload shape", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(<TenantCreateForm onSubmit={onSubmit} isSubmitting={false} submitError={null} />);

    await user.type(screen.getByLabelText(/^email/i), "newtenant@example.com");
    await user.type(screen.getByLabelText(/^password/i), "SecurePass123!");
    await user.type(screen.getByLabelText("First name"), "John");
    await user.type(screen.getByLabelText("Last name"), "Kamau");
    await user.type(screen.getByLabelText("National ID"), "12345678");
    await user.click(screen.getByRole("button", { name: /create tenant/i }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        email: "newtenant@example.com",
        password: "SecurePass123!",
        first_name: "John",
        last_name: "Kamau",
        national_id: "12345678",
      })
    );
  });

  it("shows field-level errors from the backend", () => {
    render(
      <TenantCreateForm
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={makeAxiosError({ email: ["A user with this email already exists."] })}
      />
    );

    expect(screen.getByText("A user with this email already exists.")).toBeInTheDocument();
  });
});