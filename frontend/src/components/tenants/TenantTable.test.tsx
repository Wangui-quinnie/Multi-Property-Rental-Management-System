import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { TenantTable } from "./TenantTable";
import type { Tenant } from "@/api/tenants";

const sampleTenant: Tenant = {
  id: "tenant-1",
  email: "john@example.com",
  full_name: "John Kamau",
  phone_number: "0700000000",
  national_id: "12345678",
  emergency_contact_name: "Jane Doe",
  emergency_contact_phone: "0711111111",
  status: "ACTIVE",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("TenantTable", () => {
  it("renders a row per tenant with their details", () => {
    render(<TenantTable tenants={[sampleTenant]} isLoading={false} onEdit={vi.fn()} />);

    expect(screen.getByText("John Kamau")).toBeInTheDocument();
    expect(screen.getByText("john@example.com")).toBeInTheDocument();
    expect(screen.getByText("12345678")).toBeInTheDocument();
    expect(screen.getByText("ACTIVE")).toBeInTheDocument();
  });

  it("shows an empty-state message when there are no tenants", () => {
    render(<TenantTable tenants={[]} isLoading={false} onEdit={vi.fn()} />);
    expect(screen.getByText("No tenants yet.")).toBeInTheDocument();
  });

  it("calls onEdit with the tenant when its Edit button is clicked", async () => {
    const onEdit = vi.fn();
    const user = userEvent.setup();

    render(<TenantTable tenants={[sampleTenant]} isLoading={false} onEdit={onEdit} />);
    await user.click(screen.getByRole("button", { name: /edit/i }));

    expect(onEdit).toHaveBeenCalledWith(sampleTenant);
  });
});