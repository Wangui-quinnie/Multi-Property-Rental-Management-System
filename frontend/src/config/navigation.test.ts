import { describe, it, expect } from "vitest";
import { getNavItems } from "./navigation";

describe("getNavItems", () => {
  it("returns the Admin nav set", () => {
    const labels = getNavItems("ADMIN").map((i) => i.label);
    expect(labels).toEqual([
      "Dashboard",
      "Properties",
      "Tenants",
      "Leases",
      "Vacancy",
      "Billing",
      "Payments",
      "Reports",
    ]);
  });

  it("returns the Landlord nav set (Admin's minus Tenants, plus Units)", () => {
    // Tenants is deliberately excluded here - TenantViewSet is Admin-only
    // (IsAdmin, not IsAdminOrLandlord), so a Landlord nav link to it
    // would just redirect them away. Leases/Vacancy ARE shared with
    // Admin (both viewsets' permissions fully allow Admin too).
    const labels = getNavItems("LANDLORD").map((i) => i.label);
    expect(labels).toEqual([
      "Dashboard",
      "Properties",
      "Units",
      "Leases",
      "Vacancy",
      "Billing",
      "Payments",
      "Reports",
    ]);
  });

  it("returns the Tenant nav set", () => {
    const labels = getNavItems("TENANT").map((i) => i.label);
    expect(labels).toEqual(["My Lease", "Invoices", "Payments", "Receipts", "Profile"]);
  });

  it("returns an empty array for an unknown/undefined role", () => {
    expect(getNavItems(undefined)).toEqual([]);
  });

  it("every nav item has a unique `to` path within its role's set", () => {
    (["ADMIN", "LANDLORD", "TENANT"] as const).forEach((role) => {
      const paths = getNavItems(role).map((i) => i.to);
      expect(new Set(paths).size).toBe(paths.length);
    });
  });
});