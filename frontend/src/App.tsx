import ScrollToTop from "./components/ScrollToTop";
import AppRoutes from "./routes/AppRoutes";
import { LoadingProvider } from "./contexts/LoadingContext";

function App() {
  return (
    <LoadingProvider>
      <ScrollToTop />
      <AppRoutes />
    </LoadingProvider>
  );
}

export default App;
