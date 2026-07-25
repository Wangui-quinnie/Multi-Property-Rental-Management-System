import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError, AxiosHeaders } from "axios";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { PropertyForm } from "./PropertyForm";
import { useAuth } from "@/auth/useAuth";
import { useLandlords } from "@/hooks/useLandlords";
import type { Property } from "@/api/properties";

function makeAxiosError(data: unknown) {
  return new AxiosError("Request failed", "ERR_BAD_REQUEST", undefined, undefined, {
    status: 400,
    statusText: "Bad Request",
    headers: {},
    config: { headers: new AxiosHeaders() },
    data,
  });
}

vi.mock("@/auth/useAuth");
vi.mock("@/hooks/useLandlords");

const mockedUseAuth = vi.mocked(useAuth);
const mockedUseLandlords = vi.mocked(useLandlords);

const baseAuth = { isLoading: false, login: vi.fn(), logout: vi.fn() };

const sampleProperty: Property = {
  id: "11111111-1111-1111-1111-111111111111",
  landlord: "22222222-2222-2222-2222-222222222222",
  landlord_name: "Ada Landlord",
  name: "Sunset Apartments",
  code: "SUN-001",
  location: "Nairobi",
  address: "123 Sunset Rd",
  status: "ACTIVE",
  is_archived: false,
  archived_at: null,
  total_units: 10,
  occupied_units: 8,
  vacant_units: 2,
  maintenance_units: 0,
  potential_monthly_rent: "100000.00",
  occupancy_rate: 80,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("PropertyForm", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset();
    mockedUseLandlords.mockReset();
    mockedUseLandlords.mockReturnValue({ data: [] } as never);
  });

  it("shows the code field and landlord picker for an Admin creating a property", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "admin@b.com", role: "ADMIN" },
      ...baseAuth,
    });
    mockedUseLandlords.mockReturnValue({
      data: [{ id: "landlord-1", full_name: "Ada Landlord", email: "ada@b.com" }],
    } as never);

    render(<PropertyForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);

    // Code is required, so its accessible label text is actually
    // "Code *" (see FormField's required asterisk) - match with a
    // regex rather than an exact string, same convention as Name/Location.
    expect(screen.getByLabelText(/^code/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Landlord")).toBeInTheDocument();
    expect(screen.getByText("Ada Landlord")).toBeInTheDocument();
  });

  it("shows the code field but NOT the landlord picker for a Landlord creating a property", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "2", email: "landlord@b.com", role: "LANDLORD" },
      ...baseAuth,
    });

    render(<PropertyForm onSubmit={vi.fn()} isSubmitting={false} submitError={null} />);

    expect(screen.getByLabelText(/^code/i)).toBeInTheDocument();
    expect(screen.queryByLabelText("Landlord")).not.toBeInTheDocument();
  });

  it("hides the code field and landlord picker when editing, even for Admin", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "admin@b.com", role: "ADMIN" },
      ...baseAuth,
    });

    render(
      <PropertyForm
        property={sampleProperty}
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={null}
      />
    );

    expect(screen.queryByLabelText(/^code/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Landlord")).not.toBeInTheDocument();
    // Name/Location are required, so their accessible label text is
    // actually "Name *"/"Location *" (see FormField's required asterisk) -
    // match with a case-insensitive regex rather than an exact string,
    // same convention used in Login.test.tsx.
    expect(screen.getByLabelText(/^name/i)).toHaveValue("Sunset Apartments");
    expect(screen.getByLabelText(/^location/i)).toHaveValue("Nairobi");
  });

  it("submits the create shape (name/code/location/address/status) when creating", async () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "2", email: "landlord@b.com", role: "LANDLORD" },
      ...baseAuth,
    });
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(<PropertyForm onSubmit={onSubmit} isSubmitting={false} submitError={null} />);

    await user.type(screen.getByLabelText(/^name/i), "New Property");
    await user.type(screen.getByLabelText(/^code/i), "NP-001");
    await user.type(screen.getByLabelText(/^location/i), "Mombasa");
    await user.click(screen.getByRole("button", { name: /create property/i }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ name: "New Property", code: "NP-001", location: "Mombasa" })
    );
  });

  it("submits the update shape (no code/landlord) when editing", async () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "admin@b.com", role: "ADMIN" },
      ...baseAuth,
    });
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(
      <PropertyForm
        property={sampleProperty}
        onSubmit={onSubmit}
        isSubmitting={false}
        submitError={null}
      />
    );

    await user.click(screen.getByRole("button", { name: /save changes/i }));

    const submitted = onSubmit.mock.calls[0][0];
    expect(submitted).not.toHaveProperty("code");
    expect(submitted).not.toHaveProperty("landlord");
    expect(submitted.name).toBe("Sunset Apartments");
  });

  it("shows field-level errors from the backend", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "2", email: "landlord@b.com", role: "LANDLORD" },
      ...baseAuth,
    });

    render(
      <PropertyForm
        onSubmit={vi.fn()}
        isSubmitting={false}
        submitError={makeAxiosError({ code: ["Property with this code already exists."] })}
      />
    );

    expect(screen.getByText("Property with this code already exists.")).toBeInTheDocument();
  });
});