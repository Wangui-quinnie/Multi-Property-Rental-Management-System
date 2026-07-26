import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ProfileForm } from "./ProfileForm";
import { useUpdateProfile } from "@/hooks/useProfile";
import type { Profile } from "@/api/profile";

vi.mock("@/hooks/useProfile");
vi.mock("@/components/ui/toast", () => ({ toast: { add: vi.fn() } }));

const mockedUseUpdateProfile = vi.mocked(useUpdateProfile);

const sampleProfile: Profile = {
  id: "user-1",
  email: "tenant@example.com",
  username: "tenant1",
  first_name: "John",
  last_name: "Kamau",
  full_name: "John Kamau",
  phone_number: "0712345678",
  role: "TENANT",
  is_email_verified: true,
} as Profile;

describe("ProfileForm", () => {
  beforeEach(() => {
    mockedUseUpdateProfile.mockReset();
  });

  it("pre-fills fields from the profile and shows email read-only", () => {
    mockedUseUpdateProfile.mockReturnValue({ mutateAsync: vi.fn(), isPending: false, error: null } as never);

    render(<ProfileForm profile={sampleProfile} />);

    expect(screen.getByLabelText(/^first name/i)).toHaveValue("John");
    expect(screen.getByLabelText(/^last name/i)).toHaveValue("Kamau");
    expect(screen.getByLabelText(/^phone number/i)).toHaveValue("0712345678");

    const emailField = screen.getByLabelText(/^email/i);
    expect(emailField).toHaveValue("tenant@example.com");
    expect(emailField).toBeDisabled();
  });

  it("submits the edited account fields", async () => {
    const mutateAsync = vi.fn().mockResolvedValue(sampleProfile);
    mockedUseUpdateProfile.mockReturnValue({ mutateAsync, isPending: false, error: null } as never);

    const user = userEvent.setup();
    render(<ProfileForm profile={sampleProfile} />);

    await user.clear(screen.getByLabelText(/^last name/i));
    await user.type(screen.getByLabelText(/^last name/i), "Mwangi");
    await user.click(screen.getByRole("button", { name: /save changes/i }));

    expect(mutateAsync).toHaveBeenCalledWith({
      first_name: "John",
      last_name: "Mwangi",
      phone_number: "0712345678",
    });
  });
});
