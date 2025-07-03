import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
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
const UnderConstruction = lazy(() => import("../pages/UnderConstructionPage"));

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
      {/* Authentication routes */}
      <Route path="/auth" element={withErrorBoundary(Auth)} />
      <Route
        path="/auth/google/callback"
        element={withErrorBoundary(GoogleCallback)}
      />

      {/* Public routes with MainLayout */}
      <Route element={<MainLayout />}>
        <Route path="/" element={withErrorBoundary(LandingPage)} />
        <Route path="/demo" element={withErrorBoundary(Demo)} />
        <Route path="/pricing" element={withErrorBoundary(Pricing)} />

        {/* Under construction pages */}
        <Route path="/about" element={withErrorBoundary(UnderConstruction)} />
        <Route path="/docs" element={withErrorBoundary(UnderConstruction)} />
        <Route
          path="/ai-models"
          element={withErrorBoundary(UnderConstruction)}
        />
        <Route
          path="/integrations"
          element={withErrorBoundary(UnderConstruction)}
        />
        <Route
          path="/features"
          element={withErrorBoundary(UnderConstruction)}
        />
        <Route path="/contact" element={withErrorBoundary(UnderConstruction)} />
        <Route path="/privacy" element={withErrorBoundary(UnderConstruction)} />
        <Route path="/terms" element={withErrorBoundary(UnderConstruction)} />
        <Route path="/blog" element={withErrorBoundary(UnderConstruction)} />
        <Route path="/help" element={withErrorBoundary(UnderConstruction)} />
        <Route
          path="/changelog"
          element={withErrorBoundary(UnderConstruction)}
        />
      </Route>

      {/* Protected routes with MainLayout */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="chat/:conversationId" element={withErrorBoundary(Chat)} />
        <Route path="profile" element={withErrorBoundary(Profile)} />
      </Route>

      {/* Protected dashboard routes */}
      <Route
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
          <Route
            path="settings"
            element={withErrorBoundary(UnderConstruction)}
          />
          <Route
            path="notifications"
            element={withErrorBoundary(UnderConstruction)}
          />
          <Route
            path="billing"
            element={withErrorBoundary(UnderConstruction)}
          />
        </Route>
      </Route>

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
