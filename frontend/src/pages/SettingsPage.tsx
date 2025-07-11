import { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "react-hot-toast";
import { changePassword } from "../api/api";
import { useAuthStore } from "../stores/authStore";

export default function SettingsPage() {
  const { accessToken } = useAuthStore();
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!oldPassword || !newPassword || !confirmPassword) {
      toast.error("Please fill in all fields", {
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

    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match", {
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

    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters long", {
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
      await changePassword(accessToken!, {
        old_password: oldPassword,
        new_password: newPassword,
      });

      toast.success("Password successfully changed!", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #6b46C1",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });

      // Clear form
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
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
    <div className="h-full w-full flex flex-col bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5">
      <div className="flex-1 flex flex-col p-8 space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">
            Manage your account settings and preferences
          </p>
        </div>

        {/* Password Change Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-md"
        >
          <h2 className="text-xl font-semibold text-white mb-4">
            Change Password
          </h2>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <label
                htmlFor="oldPassword"
                className="block text-sm font-medium text-gray-400 mb-1"
              >
                Current Password
              </label>
              <input
                id="oldPassword"
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-black/20 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300"
                placeholder="Enter current password"
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label
                htmlFor="newPassword"
                className="block text-sm font-medium text-gray-400 mb-1"
              >
                New Password
              </label>
              <input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-black/20 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300"
                placeholder="Enter new password"
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-gray-400 mb-1"
              >
                Confirm New Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-black/20 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300"
                placeholder="Confirm new password"
                disabled={isSubmitting}
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-4 py-3 rounded-lg bg-violet-500/20 text-violet-400 font-medium border border-violet-500/20 hover:bg-violet-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Changing Password..." : "Change Password"}
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
