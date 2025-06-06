import { Link, useNavigate } from "react-router-dom";
import Logo from "./Logo";
import { useAuthStore } from "../stores/authStore";
import { toast } from "react-hot-toast";
import { logout } from "../api/api";

export default function NavBar() {
  const { accessToken, user, clearAuth } = useAuthStore();
  const isAuthenticated = Boolean(accessToken);
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      clearAuth();
      toast.success("Logged out successfully!", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #333333",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
      navigate("/");
    } catch (error) {
      toast.error("Failed to logout. Please try again.", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #e53e3e",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
    }
  };

  return (
    <nav className="flex justify-center items-center absolute top-0 w-full backdrop-blur-3xl h-[68px] bg-[#000000]/5 z-50">
      <div className="text-white p-4 flex items-center h-[68px] w-[85%] justify-between px-[12%] relative after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-[1px] after:bg-gradient-to-r after:from-transparent after:via-white/20 after:to-transparent">
        <Link to="/" className="flex-shrink-0">
          <Logo />
        </Link>

        {/* Navigation Links */}
        <ol className="flex space-x-4">
          {isAuthenticated ? (
            <>
              <li>
                <Link
                  to="/dashboard"
                  className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                >
                  Dashboard
                </Link>
              </li>
              <li>
                <Link
                  to="dashboard/chat"
                  className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                >
                  Chats
                </Link>
              </li>
              <li>
                <Link
                  to="/pricing"
                  className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                >
                  Upgrade
                </Link>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link
                  to="/pricing"
                  className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                >
                  Pricing
                </Link>
              </li>
              <li>
                <Link
                  to="/demo"
                  className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                >
                  Demo
                </Link>
              </li>
              <li>
                <Link
                  to="/about"
                  className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                >
                  About
                </Link>
              </li>
            </>
          )}
        </ol>

        {/* Auth Buttons */}
        <ol className="flex space-x-4 items-center">
          {isAuthenticated ? (
            <>
              <li className="flex items-center gap-2">
                <Link to="/profile">
                  <span className="text-sm text-gray-300 hover:text-white transition-colors">
                    {user?.name || "Profile"}
                  </span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex-shrink-0 whitespace-nowrap text-center rounded-lg border border-white/10 bg-black/20 text-white text-sm font-medium py-1.5 px-3.5 cursor-pointer hover:bg-black/40 transition-colors"
                >
                  Sign Out
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/auth">
                  <button className="flex-shrink-0 whitespace-nowrap text-center rounded-lg bg-white text-black text-sm font-medium py-1.5 px-3.5 cursor-pointer hover:bg-gray-100 transition-colors">
                    Sign Up
                  </button>
                </Link>
              </li>
              <li>
                <Link to="/auth">
                  <button className="flex-shrink-0 whitespace-nowrap text-center rounded-lg border border-white/10 bg-black/20 text-white text-sm font-medium py-1.5 px-3.5 cursor-pointer hover:bg-black/40 transition-colors">
                    Sign In
                  </button>
                </Link>
              </li>
            </>
          )}
        </ol>
      </div>
    </nav>
  );
}
