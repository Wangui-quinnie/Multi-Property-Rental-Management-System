import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { AdminLayout } from "./AdminLayout";
import { useAuth } from "@/auth/useAuth";

vi.mock("@/auth/useAuth");

const mockedUseAuth = vi.mocked(useAuth);

function renderLayout() {
  return render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <Routes>
        <Route element={<AdminLayout />}>
          <Route path="/dashboard" element={<div>Dashboard Body</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

describe("AdminLayout", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset();
  });

  it("shows the Admin nav set for an Admin user", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "admin@b.com", role: "ADMIN" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLayout();

    expect(screen.getByRole("link", { name: /properties/i })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /units/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /leases/i })).not.toBeInTheDocument();
    expect(screen.getByText("Dashboard Body")).toBeInTheDocument();
  });

  it("shows the Landlord nav set (Admin's + Units/Leases) for a Landlord user", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "2", email: "landlord@b.com", role: "LANDLORD" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLayout();

    expect(screen.getByRole("link", { name: /units/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /leases/i })).toBeInTheDocument();
    // Tenants is Admin-only - a Landlord nav link to it would just
    // redirect them away, so it must not appear in their sidebar.
    expect(screen.queryByRole("link", { name: /tenants/i })).not.toBeInTheDocument();
  });

  it("displays the user's name/email and role, and logs out on click", async () => {
    const logout = vi.fn();
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "admin@b.com", role: "ADMIN", full_name: "Ada Min" },
      isLoading: false,
      login: vi.fn(),
      logout,
    });

    const user = userEvent.setup();
    renderLayout();

    expect(screen.getByText(/ada min/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /logout/i }));

    expect(logout).toHaveBeenCalledTimes(1);
  });
});