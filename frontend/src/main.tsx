import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import "./styles/tailwind.css";
import "./styles/index.css";
import App from "./App.tsx";
import "nprogress/nprogress.css";
import { Toaster } from "react-hot-toast";

const router = createBrowserRouter([
  {
    path: "*",
    element: <App />,
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <Toaster />
      <RouterProvider router={router} />
    </ErrorBoundary>
  </StrictMode>
);
