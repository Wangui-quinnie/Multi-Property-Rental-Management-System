import { Outlet } from "react-router-dom";
import { useAuth } from "@/auth/useAuth";
import { Button } from "@/components/ui/button";
import { SidebarNav } from "@/components/shared/SidebarNav";
import { getNavItems } from "@/config/navigation";

export function AdminLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b bg-white px-6 py-4">
        <h1 className="text-lg font-semibold">Rental Management</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-600">
            {user?.full_name || user?.email} ({user?.role})
          </span>
          <Button variant="outline" size="sm" onClick={logout}>Logout</Button>
        </div>
      </header>
      <div className="flex">
        <aside className="hidden w-56 shrink-0 border-r bg-white md:block">
          <SidebarNav items={getNavItems(user?.role)} />
        </aside>
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}