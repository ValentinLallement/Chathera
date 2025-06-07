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

  return (
    <>
      <nav className="flex justify-center items-center fixed top-0 w-full backdrop-blur-3xl h-[68px] bg-[#000000]/5 z-50">
        <div className="text-white p-4 flex items-center h-[68px] w-full md:w-[85%] justify-between px-4 md:px-[12%] relative after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-[1px] after:bg-gradient-to-r after:from-transparent after:via-white/20 after:to-transparent">
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

          {/* Desktop Auth Buttons */}
          <ol className="hidden md:flex space-x-4 items-center">
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
                  open: { rotate: -45, y: -6 },
                }}
                transition={{ duration: 0.3 }}
              />
            </motion.div>
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-40 md:hidden"
          >
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0 bg-black/95 backdrop-blur-xl"
              onClick={() => setIsMobileMenuOpen(false)}
            />

            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 20 }}
              className="absolute inset-y-0 right-0 w-full max-w-sm bg-gradient-to-b from-zinc 900/50 to-black/50 backdrop-blur-xl p-6 flex flex-col justify-between"
              onClick={(e) => e.stopPropagation()}
            >
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
                    onClick={() => {
                      handleLogout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="w-full text-center rounded-lg border border-white/10 bg-black/20 text-white text-base font-medium py-3 px-4 hover:bg-black/40 transition-colors"
                  >
                    Sign Out
                  </button>
                ) : (
                  <>
                    <Link
                      to="/auth"
                      className="w-full text-center rounded-lg bg-white text-black text-base font-medium py-3 px-4 hover:bg-gray-100 transition-colors"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Sign Up
                    </Link>
                    <Link
                      to="/auth"
                      className="w-full text-center rounded-lg border border-white/10 bg-black/20 text-white text-base font-medium py-3 px-4 hover:bg-black/40 transition-colors"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Sign In
                    </Link>
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
