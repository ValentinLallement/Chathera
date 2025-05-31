import { Outlet } from "react-router-dom";
import NavBar from "../components/NavBar";
import LoadingIndicator from "../components/LoadingIndicator";
import Footer from "../components/Footer";

export default function MainLayout() {
  return (
    <div className="flex flex-col h-screen">
      <header>
        <NavBar />
        <LoadingIndicator />
      </header>
      <main className="flex-1 p-4">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
