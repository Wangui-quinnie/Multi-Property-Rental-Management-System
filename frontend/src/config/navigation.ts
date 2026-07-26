import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Building2,
  DoorOpen,
  Users,
  ScrollText,
  Receipt,
  CreditCard,
  BarChart3,
  FileStack,
  UserCircle,
  KeyRound,
} from "lucide-react";
import type { Role } from "@/auth/AuthContext";

export interface NavItem {
  label: string;
  to: string;
  icon: LucideIcon;
}

const adminNav: NavItem[] = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
  { label: "Properties", to: "/properties", icon: Building2 },
  { label: "Tenants", to: "/tenants", icon: Users },
  { label: "Leases", to: "/leases", icon: ScrollText },
  { label: "Vacancy", to: "/vacancy", icon: KeyRound },
  { label: "Billing", to: "/billing", icon: Receipt },
  { label: "Payments", to: "/payments", icon: CreditCard },
  { label: "Reports", to: "/reports", icon: BarChart3 },
];

// Same as Admin, plus Units (Landlord manages the physical property
// directly; Admin oversees at a higher level, reaching Units only via
// a Property's detail page). Deliberately excludes Tenants -
// TenantViewSet is Admin-only (IsAdmin), so a Landlord following this
// link would just get redirected away. Leases/Vacancy ARE shared with
// Admin (LeaseViewSet's IsAdminOrLandlordWriteTenantReadOnly and
// VacancyPeriodViewSet's IsAdminOrLandlord both permit Admin fully).
const landlordNav: NavItem[] = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
  { label: "Properties", to: "/properties", icon: Building2 },
  { label: "Units", to: "/units", icon: DoorOpen },
  { label: "Leases", to: "/leases", icon: ScrollText },
  { label: "Vacancy", to: "/vacancy", icon: KeyRound },
  { label: "Billing", to: "/billing", icon: Receipt },
  { label: "Payments", to: "/payments", icon: CreditCard },
  { label: "Reports", to: "/reports", icon: BarChart3 },
];

const tenantNav: NavItem[] = [
  { label: "My Lease", to: "/portal/lease", icon: ScrollText },
  { label: "Invoices", to: "/portal/invoices", icon: Receipt },
  { label: "Payments", to: "/portal/payments", icon: CreditCard },
  { label: "Receipts", to: "/portal/receipts", icon: FileStack },
  { label: "Profile", to: "/portal/profile", icon: UserCircle },
];

export function getNavItems(role?: Role): NavItem[] {
  switch (role) {
    case "ADMIN":
      return adminNav;
    case "LANDLORD":
      return landlordNav;
    case "TENANT":
      return tenantNav;
    default:
      return [];
  }
}