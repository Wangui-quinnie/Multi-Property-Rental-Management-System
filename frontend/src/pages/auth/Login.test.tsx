import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { Login } from "./Login";
import { useAuth } from "@/auth/useAuth";

vi.mock("@/auth/useAuth");

const mockedUseAuth = vi.mocked(useAuth);

function renderLogin(initialEntry = "/login") {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<div>Dashboard Page</div>} />
        <Route path="/portal" element={<div>Portal Page</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("Login", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset();
  });

  it("shows a loader while auth state is resolving", () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      isLoading: true,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLogin();

    expect(screen.queryByText("Sign in")).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/email/i)).not.toBeInTheDocument();
  });

  it("redirects an already-authenticated Admin/Landlord to /dashboard", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", email: "a@b.com", role: "ADMIN" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLogin();

    expect(screen.getByText("Dashboard Page")).toBeInTheDocument();
  });

  it("redirects an already-authenticated Tenant to /portal", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "2", email: "t@b.com", role: "TENANT" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLogin();

    expect(screen.getByText("Portal Page")).toBeInTheDocument();
  });

  it("renders the sign-in form when there is no authenticated user", () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLogin();

    // CardTitle renders a plain <div> (data-slot="card-title"), not a
    // semantic heading, so assert on text content rather than role. The
    // submit button also reads "Sign in", so scope to the title element.
    expect(
      screen.getByText("Sign in", { selector: '[data-slot="card-title"]' })
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("logs in and navigates to /dashboard on successful submit", async () => {
    const login = vi.fn().mockResolvedValue(undefined);
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login, logout: vi.fn() });

    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/password/i), "secret");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(login).toHaveBeenCalledWith("a@b.com", "secret");
    expect(await screen.findByText("Dashboard Page")).toBeInTheDocument();
  });

  it("shows an error alert when login fails", async () => {
    const login = vi.fn().mockRejectedValue(new Error("bad credentials"));
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login, logout: vi.fn() });

    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/password/i), "wrong");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument();
  });
});
