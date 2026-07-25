import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import { LayoutDashboard, Building2 } from "lucide-react";
import { SidebarNav } from "./SidebarNav";
import type { NavItem } from "@/config/navigation";

const items: NavItem[] = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
  { label: "Properties", to: "/properties", icon: Building2 },
];

describe("SidebarNav", () => {
  it("renders a link for every nav item with the correct href", () => {
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <SidebarNav items={items} />
      </MemoryRouter>
    );

    expect(screen.getByRole("link", { name: /dashboard/i })).toHaveAttribute("href", "/dashboard");
    expect(screen.getByRole("link", { name: /properties/i })).toHaveAttribute("href", "/properties");
  });

  it("highlights the link matching the current route", () => {
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <SidebarNav items={items} />
      </MemoryRouter>
    );

    expect(screen.getByRole("link", { name: /dashboard/i })).toHaveClass("bg-slate-900");
    expect(screen.getByRole("link", { name: /properties/i })).not.toHaveClass("bg-slate-900");
  });
});
