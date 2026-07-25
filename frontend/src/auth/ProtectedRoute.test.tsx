import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ProtectedRoute } from "./ProtectedRoute";
import { useAuth } from "./useAuth";

vi.mock("./useAuth");

const mockedUseAuth = vi.mocked(useAuth);

function renderProtected(allowedRoles?: ("ADMIN" | "LANDLORD" | "TENANT")[]) {
  return render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route path="/" element={<div>Landing Page</div>} />
        <Route element={<ProtectedRoute allowedRoles={allowedRoles} />}>
          <Route path="/dashboard" element={<div>Protected Content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset();
  });

  it("shows a loader while auth state is resolving", () => {
    mockedUseAuth.mockReturnValue({ user: null, isLoading: true, login: vi.fn(), logout: vi.fn() });

    renderProtected();

    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    expect(screen.queryByText("Login Page")).not.toBeInTheDocument();
  });

  it("redirects to /login when there is no user", () => {
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login: vi.fn(), logout: vi.fn() });

    renderProtected();

    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("redirects to / when the user's role isn't allowed", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "t@b.com", role: "TENANT" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderProtected(["ADMIN", "LANDLORD"]);

    expect(screen.getByText("Landing Page")).toBeInTheDocument();
  });

  it("renders the nested route when the user's role is allowed", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "a@b.com", role: "ADMIN" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderProtected(["ADMIN", "LANDLORD"]);

    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });
});
