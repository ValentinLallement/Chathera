import ScrollToTop from "./components/ScrollToTop";
import AppRoutes from "./routes/AppRoutes";
import { LoadingProvider } from "./contexts/LoadingContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ReactQueryDevtools />
      <LoadingProvider>
        <ScrollToTop />
        <AppRoutes />
      </LoadingProvider>
    </QueryClientProvider>
  );
}

export default App;
