import { Link, useNavigate } from "react-router-dom";
import Logo from "./Logo";
import { useAuthStore } from "../stores/authStore";
import { useSidebarStore } from "../stores/sidebarStore";
import { toast } from "react-hot-toast";
import { logout } from "../api/api";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

export default function NavBar() {
  const { accessToken, user, clearAuth } = useAuthStore();
  const { setOpen } = useSidebarStore();
  const isAuthenticated = Boolean(accessToken);
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      setOpen(false);
      clearAuth();
      setIsMobileMenuOpen(false);

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

  const navigateToAuth = (isSignUp: boolean) => {
    navigate("/auth", { state: { isSignUp } });
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex-shrink-0">
              <Logo />
            </Link>

            {/* Desktop Navigation */}
            <ol className="hidden md:flex space-x-4">
              {isAuthenticated ? (
                <>
                  <li>
                    <Link
                      to="/dashboard"
                      className="text-white group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                    >
                      Dashboard
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/dashboard/chat"
                      className="text-white group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                    >
                      Chats
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/pricing"
                      className="text-white group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
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
                      className="text-white group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                    >
                      Pricing
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/demo"
                      className="text-white group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                    >
                      Demo
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/about"
                      className="text-white group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:text-violet-400"
                    >
                      About
                    </Link>
                  </li>
                </>
              )}
            </ol>

            {/* Desktop Auth Buttons */}
            <ol className="hidden md:flex space-x-4 items-center">
              {isAuthenticated ? (
                <>
                  <li className="flex items-center gap-2">
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
                    <button
                      onClick={() => navigateToAuth(true)}
                      className="flex-shrink-0 whitespace-nowrap text-center rounded-lg bg-white text-black text-sm font-medium py-1.5 px-3.5 cursor-pointer hover:bg-gray-100 transition-colors"
                    >
                      Sign Up
                    </button>
                  </li>
                  <li>
                    <button
                      onClick={() => navigateToAuth(false)}
                      className="flex-shrink-0 whitespace-nowrap text-center rounded-lg border border-white/10 bg-black/20 text-white text-sm font-medium py-1.5 px-3.5 cursor-pointer hover:bg-black/40 transition-colors"
                    >
                      Sign In
                    </button>
                  </li>
                </>
              )}
            </ol>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden relative z-50 w-8 h-8 flex items-center justify-center"
            >
              <motion.div
                className="w-6 h-6 flex flex-col justify-center items-center"
                initial={false}
                animate={isMobileMenuOpen ? "open" : "closed"}
              >
                <motion.span
                  className="w-full h-[2px] bg-white mb-1.5 block"
                  variants={{
                    closed: { rotate: 0, y: 0 },
                    open: { rotate: 45, y: 6 },
                  }}
                  transition={{ duration: 0.3 }}
                />
                <motion.span
                  className="w-full h-[2px] bg-white block"
                  variants={{
                    closed: { opacity: 1 },
                    open: { opacity: 0 },
                  }}
                  transition={{ duration: 0.3 }}
                />
                <motion.span
                  className="w-full h-[2px] bg-white mt-1.5 block"
                  variants={{
                    closed: { rotate: 0, y: 0 },
                    open: { rotate: -45, y: -10 },
                  }}
                  transition={{ duration: 0.3 }}
                />
              </motion.div>
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 md:hidden"
          >
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 bg-black/90 backdrop-blur-xl"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <motion.div className="relative bg-transparent min-h-screen px-6 py-6">
              <div className="flex flex-col space-y-4 mt-16">
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/dashboard"
                      className="text-lg font-medium text-white hover:text-violet-400 transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="dashboard/chat"
                      className="text-lg font-medium text-white hover:text-violet-400 transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Chats
                    </Link>
                    <Link
                      to="/pricing"
                      className="text-lg font-medium text-white hover:text-violet-400 transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Upgrade
                    </Link>
                    <Link
                      to="/profile"
                      className="text-lg font-medium text-white hover:text-violet-400 transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      {user?.name || "Profile"}
                    </Link>
                  </>
                ) : (
                  <>
                    <Link
                      to="/pricing"
                      className="text-lg font-medium text-white hover:text-violet-400 transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Pricing
                    </Link>
                    <Link
                      to="/demo"
                      className="text-lg font-medium text-white hover:text-violet-400 transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Demo
                    </Link>
                    <Link
                      to="/about"
                      className="text-lg font-medium text-white hover:text-violet-400 transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      About
                    </Link>
                  </>
                )}
              </div>

              <div className="flex flex-col space-y-4 pt-4 border-t border-white/10">
                {isAuthenticated ? (
                  <button
                    onClick={handleLogout}
                    className="w-full text-center rounded-lg border border-white/10 bg-black/20 text-white text-base font-medium py-3 px-4 hover:bg-black/40 transition-colors"
                  >
                    Sign Out
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => navigateToAuth(true)}
                      className="w-full text-center rounded-lg bg-white text-black text-base font-medium py-3 px-4 hover:bg-gray-100 transition-colors"
                    >
                      Sign Up
                    </button>
                    <button
                      onClick={() => navigateToAuth(false)}
                      className="w-full text-center rounded-lg border border-white/10 bg-black/20 text-white text-base font-medium py-3 px-4 hover:bg-black/40 transition-colors"
                    >
                      Sign In
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
