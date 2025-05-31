import { Outlet } from "react-router-dom";
import NavBar from "../components/NavBar";
import LoadingIndicator from "../components/LoadingIndicator";
import Footer from "../components/Footer";

export default function MainLayout() {
  return (
    <div className="flex flex-col bg-main-bg h-fit min-h-screen no-scrollbar">
      <header className="fixed top-0 left-0 w-full z-50">
        <NavBar />
        <LoadingIndicator />
      </header>
      <main className="flex-1 h-fit no-scrollbar">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
