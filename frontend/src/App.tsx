import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/auth/AuthContext";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Landing } from "@/pages/Landing";
import { Login } from "@/pages/auth/Login";
import { Dashboard } from "@/pages/Dashboard";
import { NotFound } from "@/pages/NotFound";
import { AdminLayout } from "@/layouts/AdminLayout";
import { TenantLayout } from "@/layouts/TenantLayout";
import { Toaster } from "@/components/ui/toast";
import { PropertiesPage } from "@/pages/properties/PropertiesPage";
import { PropertyCreatePage } from "@/pages/properties/PropertyCreatePage";
import { PropertyDetailPage } from "@/pages/properties/PropertyDetailPage";
import { PropertyEditPage } from "@/pages/properties/PropertyEditPage";
import { UnitsPage } from "@/pages/units/UnitsPage";
import { TenantsPage } from "@/pages/tenants/TenantsPage";
import { TenantCreatePage } from "@/pages/tenants/TenantCreatePage";
import { LeasesPage } from "@/pages/leases/LeasesPage";
import { LeaseCreatePage } from "@/pages/leases/LeaseCreatePage";
import { LeaseEditPage } from "@/pages/leases/LeaseEditPage";
import { VacancyPage } from "@/pages/vacancy/VacancyPage";
import { BillingPage } from "@/pages/billing/BillingPage";
import { PaymentsPage } from "@/pages/payments/PaymentsPage";
import { ReportsPage } from "@/pages/reports/ReportsPage";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Toaster />
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />

            <Route element={<ProtectedRoute allowedRoles={["ADMIN", "LANDLORD"]} />}>
              <Route element={<AdminLayout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/properties" element={<PropertiesPage />} />
                <Route path="/properties/new" element={<PropertyCreatePage />} />
                <Route path="/properties/:id" element={<PropertyDetailPage />} />
                <Route path="/properties/:id/edit" element={<PropertyEditPage />} />
                <Route path="/units" element={<UnitsPage />} />
                <Route path="/leases" element={<LeasesPage />} />
                <Route path="/leases/new" element={<LeaseCreatePage />} />
                <Route path="/leases/:id/edit" element={<LeaseEditPage />} />
                <Route path="/vacancy" element={<VacancyPage />} />
                <Route path="/billing" element={<BillingPage />} />
                <Route path="/payments" element={<PaymentsPage />} />
                <Route path="/reports" element={<ReportsPage />} />
              </Route>
            </Route>

            {/* Tenants is Admin-only (TenantViewSet uses IsAdmin, not
                IsAdminOrLandlord) - a separate route group rather than
                folding it into the Admin+Landlord group above. */}
            <Route element={<ProtectedRoute allowedRoles={["ADMIN"]} />}>
              <Route element={<AdminLayout />}>
                <Route path="/tenants" element={<TenantsPage />} />
                <Route path="/tenants/new" element={<TenantCreatePage />} />
              </Route>
            </Route>

            <Route element={<ProtectedRoute allowedRoles={["TENANT"]} />}>
              <Route element={<TenantLayout />}>
                <Route path="/portal" element={<Dashboard />} />
              </Route>
            </Route>

            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}