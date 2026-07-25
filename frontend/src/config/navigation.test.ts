import { describe, it, expect } from "vitest";
import { getNavItems } from "./navigation";

describe("getNavItems", () => {
  it("returns the Admin nav set", () => {
    const labels = getNavItems("ADMIN").map((i) => i.label);
    expect(labels).toEqual([
      "Dashboard",
      "Properties",
      "Tenants",
      "Billing",
      "Payments",
      "Reports",
    ]);
  });

  it("returns the Landlord nav set: Admin's items plus Units and Leases", () => {
    const adminLabels = getNavItems("ADMIN").map((i) => i.label);
    const landlordLabels = getNavItems("LANDLORD").map((i) => i.label);

    adminLabels.forEach((label) => expect(landlordLabels).toContain(label));
    expect(landlordLabels).toContain("Units");
    expect(landlordLabels).toContain("Leases");
    expect(landlordLabels.length).toBe(adminLabels.length + 2);
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
