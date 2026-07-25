import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { TenantLayout } from "./TenantLayout";
import { useAuth } from "@/auth/useAuth";

vi.mock("@/auth/useAuth");

const mockedUseAuth = vi.mocked(useAuth);

function renderLayout() {
  return render(
    <MemoryRouter initialEntries={["/portal"]}>
      <Routes>
        <Route element={<TenantLayout />}>
          <Route path="/portal" element={<div>Portal Body</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

describe("TenantLayout", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset();
  });

  it("shows the Tenant nav set", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "3", email: "tenant@b.com", role: "TENANT" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLayout();

    expect(screen.getByRole("link", { name: /my lease/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /invoices/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /receipts/i })).toBeInTheDocument();
    expect(screen.getByText("Portal Body")).toBeInTheDocument();
  });

  it("displays the user's name/email and logs out on click", async () => {
    const logout = vi.fn();
    mockedUseAuth.mockReturnValue({
      user: { id: "3", email: "tenant@b.com", role: "TENANT" },
      isLoading: false,
      login: vi.fn(),
      logout,
    });

    const user = userEvent.setup();
    renderLayout();

    expect(screen.getByText("tenant@b.com")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /logout/i }));

    expect(logout).toHaveBeenCalledTimes(1);
  });
});
