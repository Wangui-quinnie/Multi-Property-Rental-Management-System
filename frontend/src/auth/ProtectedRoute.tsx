import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./useAuth";
import type { Role } from "./AuthContext";
import { PageLoader } from "@/components/shared/PageLoader";

interface ProtectedRouteProps {
  allowedRoles?: Role[];
}

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <PageLoader fullScreen />;

  if (!user) return <Navigate to="/login" replace />;

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}