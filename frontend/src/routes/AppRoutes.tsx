import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import NotFound from "../pages/NotFound";
import LoadingIndicator from "../components/LoadingIndicator";
import ErrorBoundary from "../components/ErrorBoundary";
import DashBoardLayout from "../layouts/DashBoardLayout";
import { ProtectedRoute } from "../components/ProtectedRoute";

// Lazy-load comme ca ya du code splitting bg :)
const LandingPage = lazy(() => import("../pages/LandingPage"));
const Home = lazy(() => import("../pages/HomePage"));
const DashBoard = lazy(() => import("../pages/DashBoardPage"));
const Chat = lazy(() => import("../pages/ChatPage"));
const Partners = lazy(() => import("../pages/PartnersPage"));
const Auth = lazy(() => import("../pages/AuthentificationPage"));
const GoogleCallback = lazy(() => import("../pages/GoogleCallback"));
const Profile = lazy(() => import("../pages/ProfilePage"));
const Demo = lazy(() => import("../pages/DemoPage"));
const Pricing = lazy(() => import("../pages/PricingPage"));
const Settings = lazy(() => import("../pages/SettingsPage"));

// Wrap lazy components with error boundary
const withErrorBoundary = (Component: React.ComponentType) => (
  <ErrorBoundary>
    <Suspense fallback={<LoadingIndicator />}>
      <Component />
    </Suspense>
  </ErrorBoundary>
);

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/auth" element={withErrorBoundary(Auth)} />
      <Route
        path="/auth/google/callback"
        element={withErrorBoundary(GoogleCallback)}
      />
      <Route path="/demo" element={withErrorBoundary(Demo)} />
      <Route path="/pricing" element={withErrorBoundary(Pricing)} />

      {/* Protected routes wrapped in MainLayout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={withErrorBoundary(LandingPage)} />
        <Route path="chat/:conversationId" element={withErrorBoundary(Chat)} />
        <Route path="profile" element={withErrorBoundary(Profile)} />
      </Route>

      {/* Protected dashboard routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashBoardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="dashboard" element={<DashBoard />}>
          <Route index element={withErrorBoundary(Home)} />
          <Route path="chat" element={withErrorBoundary(Chat)} />
          <Route path="partners" element={withErrorBoundary(Partners)} />
          <Route path="settings" element={withErrorBoundary(Settings)} />
        </Route>
      </Route>

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
