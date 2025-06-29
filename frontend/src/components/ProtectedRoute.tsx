import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuthStore();
  const location = useLocation();

  if (!accessToken) {
    // Redirect to auth page but save the attempted location
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
