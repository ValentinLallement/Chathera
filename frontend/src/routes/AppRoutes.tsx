import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import NotFound from "../pages/NotFound";
import LoadingIndicator from "../components/LoadingIndicator";
import ErrorBoundary from "../components/ErrorBoundary";
import DashBoardLayout from "../layouts/DashBoardLayout";

// Lazy-load comme ca ya du code splitting bg :)
const LandingPage = lazy(() => import("../pages/LandingPage"));
const Home = lazy(() => import("../pages/HomePage"));
const DashBoard = lazy(() => import("../pages/DashBoardPage"));
const Chat = lazy(() => import("../pages/ChatPage"));
const Girls = lazy(() => import("../pages/GirlsPage"));
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

      {/* A "protected" area wrapped by MainLayout */}
      <Route path="/" element={<MainLayout />}>
        {/* Index route, i.e. "/" */}
        <Route index element={withErrorBoundary(LandingPage)} />

        {/* ex: /chat/1234 en tant que props*/}
        <Route path="chat/:conversationId" element={withErrorBoundary(Chat)} />

        <Route path="profile" element={withErrorBoundary(Profile)} />
        <Route path="demo" element={withErrorBoundary(Demo)} />
        <Route path="pricing" element={withErrorBoundary(Pricing)} />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Route>

      <Route path="/" element={<DashBoardLayout />}>
        <Route path="dashboard" element={<DashBoard />}>
          <Route index element={withErrorBoundary(Home)} />
          <Route path="chat" element={withErrorBoundary(Chat)} />
          <Route path="girls" element={withErrorBoundary(Girls)} />
          <Route path="settings" element={withErrorBoundary(Settings)} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Route>

      {/* Redirect any unknown route (that didn't match "/" subtree) to "/" or 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
