import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import NotFound from "../pages/NotFound";
import LoadingIndicator from "../components/LoadingIndicator";
import ErrorBoundary from "../components/ErrorBoundary";

// Lazy-load comme ca ya du code splitting bg :)
const LandingPage = lazy(() => import("../pages/LandingPage"));
const Home = lazy(() => import("../pages/HomePage"));
const Chat = lazy(() => import("../pages/ChatPage"));
const Login = lazy(() => import("../pages/AuthentificationPage"));
const Profile = lazy(() => import("../pages/ProfilePage"));
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
      <Route path="/login" element={withErrorBoundary(Login)} />
      <Route path="/settings" element={withErrorBoundary(Settings)} />

      {/* A "protected" area wrapped by MainLayout */}
      <Route path="/" element={<MainLayout />}>
        {/* Index route, i.e. "/" */}
        <Route index element={withErrorBoundary(LandingPage)} />

        {/* Home page when logged in */}
        <Route path="home" element={withErrorBoundary(Home)} />

        {/* ex: /chat/1234 en tant que props*/}
        <Route path="chat/:conversationId" element={withErrorBoundary(Chat)} />

        <Route path="profile" element={withErrorBoundary(Profile)} />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Route>

      {/* Redirect any unknown route (that didn't match "/" subtree) to "/" or 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
