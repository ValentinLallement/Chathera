import { useState } from "react";
import { motion } from "framer-motion";
import { HiChevronLeft } from "react-icons/hi";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import StarLogo from "../assets/images/StarLogo.webp";
import Title from "../components/Title";
import { requestPasswordReset } from "../api/api";

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email.trim()) {
      toast.error("Please enter your email address", {
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
      return;
    }

    setIsSubmitting(true);
    try {
      await requestPasswordReset({ email });
      toast.success("If an account exists with this email, you will receive a password reset link.", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #6b46C1",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem"
        }
      });
      // Navigate back to login after showing success message
      setTimeout(() => navigate("/auth"), 3000);
    } catch (error: any) {
      toast.error(error.message || "An error occurred", {
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
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 bg-gradient-to-b from-zinc-900/5 to-black/5 flex items-center justify-center px-4 py-8">
      <Title>Reset Password - Chathera</Title>
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[25%] -left-[25%] w-[150%] h-[150%] bg-gradient-conic from-violet-500/10 via-transparent to-transparent opacity-10 animate-slow-spin"></div>
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_800px_at_50%_50%,rgba(147,51,234,0.02),transparent)] animate-pulse"></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative w-full max-w-md"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-zinc-500/5 to-zinc-400/5 rounded-2xl blur-2xl transform scale-105"></div>
        <div className="relative space-y-8 bg-black/20 backdrop-blur-xl p-8 rounded-2xl border border-white/5 shadow-2xl">
          <button
            onClick={() => navigate("/auth")}
            className="absolute top-4 left-4 p-2 rounded-full bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors text-gray-400 hover:text-gray-300"
            aria-label="Go back"
          >
            <HiChevronLeft className="w-5 h-5" />
          </button>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center space-y-2"
          >
            <div className="flex justify-center mb-4">
              <img src={StarLogo} alt="StarLogo" className="w-8 h-8" />
            </div>
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-gray-200 to-white">
              Reset Password
            </h2>
            <p className="text-gray-400">
              Enter your email address and we'll send you a link to reset your password
            </p>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-4"
            onSubmit={handleSubmit}
          >
            <div className="group">
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-black/20 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300"
                placeholder="Enter your email"
                disabled={isSubmitting}
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="relative w-full px-4 py-3 rounded-lg overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-violet-600/80 to-violet-700/80 transition-transform duration-300 group-hover:scale-[1.02]"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-violet-600/50 to-violet-700/50 opacity-50 blur-xl transition-transform duration-300 group-hover:scale-110"></div>
              <span className="relative text-white font-medium">
                {isSubmitting ? "Sending..." : "Send Reset Link"}
              </span>
            </button>
          </motion.form>

          <p className="text-center text-sm text-gray-400">
            Remember your password?{" "}
            <button
              onClick={() => navigate("/auth")}
              className="text-violet-400 hover:text-violet-300 transition-colors hover:underline"
            >
              Sign in
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
}