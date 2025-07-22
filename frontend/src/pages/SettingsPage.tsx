import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";
import { changePassword } from "../api/api";
import { useAuthStore } from "../stores/authStore";
import { useGetSubscriptionInfos, useOpenCustomerPortal, useCancelSubscription } from "../hooks/useApi";
import { ChevronDown, ChevronUp } from "lucide-react";

export default function SettingsPage() {
  const { accessToken } = useAuthStore();

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const { data: subscriptionData, isLoading, error } = useGetSubscriptionInfos();

  // Nouveaux hooks mutation
  const openCustomerPortal = useOpenCustomerPortal();
  const cancelSubscription = useCancelSubscription();

  const handlePasswordChange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!oldPassword || !newPassword || !confirmPassword) {
      toast.error("Please fill in all fields", { style: toastStyle("error") });
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match", { style: toastStyle("error") });
      return;
    }
    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters long", { style: toastStyle("error") });
      return;
    }

    setIsSubmitting(true);
    try {
      await changePassword(accessToken!, {
        old_password: oldPassword,
        new_password: newPassword,
      });
      toast.success("Password successfully changed!", { style: toastStyle("success") });

      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setShowPasswordForm(false);
    } catch (error: any) {
      toast.error(error.message || "An error occurred", { style: toastStyle("error") });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Gestion clic bouton "Change Information"
  const handleChangeInfoClick = async () => {
    try {
      const response = await openCustomerPortal.mutateAsync();
      if (response?.url) {
        window.open(response.url, "_blank");
      } else {
        toast.error("No URL returned from customer portal");
      }
    } catch {
      // erreur déjà gérée dans useMutation
    }
  };

  // Gestion clic bouton "Cancel Subscription"
  const handleCancelClick = async () => {
    const userConfirmed = window.confirm(
      "Are you sure you want to cancel your subscription? This action cannot be undone."
    );
    if (!userConfirmed) return; // Annule la fonction si l’utilisateur refuse

    try {
      await cancelSubscription.mutateAsync();
      toast.success("Subscription canceled");
      // Ici tu peux aussi rafraîchir les infos d'abonnement si nécessaire
    } catch {
      // erreur déjà gérée dans useMutation
    }
  };

  return (
    <div className="h-full w-full flex bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5">
      {/* Colonne gauche : paramètres */}
      <div className="flex-1 flex flex-col p-8 space-y-8 max-w-xl">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account settings and preferences</p>
        </div>

        <div className="w-full">
          <button
            onClick={() => setShowPasswordForm((prev) => !prev)}
            className="w-full flex justify-between items-center px-5 py-3 rounded-lg bg-violet-500/20 text-violet-400 font-medium border border-violet-500/20 hover:bg-violet-500/30 transition-colors"
          >
            <span>Change my password</span>
            {showPasswordForm ? (
              <ChevronUp className="h-5 w-5 text-violet-400" />
            ) : (
              <ChevronDown className="h-5 w-5 text-violet-400" />
            )}
          </button>
        </div>

        <AnimatePresence>
          {showPasswordForm && (
            <motion.div
              key="passwordForm"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.4 }}
              className="overflow-hidden"
            >
              <form onSubmit={handlePasswordChange} className="space-y-4 mt-4">
                <InputField
                  id="oldPassword"
                  label="Current Password"
                  value={oldPassword}
                  onChange={setOldPassword}
                  disabled={isSubmitting}
                />
                <InputField
                  id="newPassword"
                  label="New Password"
                  value={newPassword}
                  onChange={setNewPassword}
                  disabled={isSubmitting}
                />
                <InputField
                  id="confirmPassword"
                  label="Confirm New Password"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  disabled={isSubmitting}
                />

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full px-4 py-3 rounded-lg bg-violet-500/20 text-violet-400 font-medium border border-violet-500/20 hover:bg-violet-500/30 transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Changing Password..." : "Change Password"}
                </button>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Colonne droite : abonnement stylée et animée */}
      <div className="hidden lg:flex flex-1 p-8">
        <SubscriptionInfoCard
          data={subscriptionData}
          loading={isLoading}
          error={error}
          onChangeInfoClick={handleChangeInfoClick}
          onCancelClick={handleCancelClick}
          loadingChangeInfo={openCustomerPortal.status === "pending"}
          loadingCancel={cancelSubscription.status === "pending"}
        />
      </div>
    </div>
  );
}

function InputField({ id, label, value, onChange, disabled }: any) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-400 mb-1">
        {label}
      </label>
      <input
        id={id}
        type="password"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={inputStyle}
        placeholder={`Enter ${label.toLowerCase()}`}
        disabled={disabled}
      />
    </div>
  );
}

function SubscriptionInfoCard({
  data,
  loading,
  error,
  onChangeInfoClick,
  onCancelClick,
  loadingChangeInfo,
  loadingCancel,
}: any) {
  if (loading) return <p className="text-gray-400">Loading subscription...</p>;
  if (error || !data?.subscriptions) return <p className="text-red-500">Error loading subscription</p>;

  const sub = data.subscriptions;

  const startDate = new Date(sub.stripe_current_period_start).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  const endDate = new Date(sub.stripe_current_period_end).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <motion.div
      className="min-h-full bg-gradient-to-b from-gray-900 to-black rounded-2xl p-8 relative overflow-hidden border border-white/10 backdrop-blur-sm w-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Background décoratif */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-pink-500/[0.02] via-violet-500/[0.015] to-transparent" />
        <div className="absolute inset-0 bg-[linear-gradient(165deg,rgba(236,72,153,0.015),transparent_70%)]" />
        <div className="absolute inset-0 bg-gradient-to-t from-transparent via-pink-500/[0.01] to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.02),transparent_70%)]" />
      </div>

      <motion.h2
        className="text-3xl font-bold text-white relative z-10 mb-8 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        Your Subscription
      </motion.h2>

      <motion.div
        className="space-y-6 relative z-10"
      >
        <InfoRow label="Plan" value={sub.plan} />
        <InfoRow label="Status" value={sub.status} />
        <InfoRow label="Remaining Messages" value={sub.remaining ?? "∞"} />
        <InfoRow label="Message Limit" value={sub.message_limit} />
        <InfoRow label="Renewal Price" value={`${sub.stripe_plan_amount_eur} ${sub.stripe_currency.toUpperCase()}`} />
        <InfoRow label="Period Start" value={startDate} />
        <InfoRow label="Period End" value={endDate} />
      </motion.div>

      <motion.div
        className="mt-12 flex justify-center gap-6 relative z-10"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <button
          type="button"
          onClick={onChangeInfoClick}
          disabled={loadingChangeInfo}
          className="px-6 py-3 rounded-lg bg-violet-500/20 text-violet-400 font-semibold border border-violet-500/20 hover:bg-violet-500/30 transition-colors shadow-md shadow-violet-500/30 disabled:opacity-50"
        >
          {loadingChangeInfo ? "Opening..." : "Change Information"}
        </button>

        <button
          type="button"
          onClick={onCancelClick}
          disabled={loadingCancel}
          className="px-6 py-3 rounded-lg bg-red-500/20 text-red-500 font-semibold border border-red-500/20 hover:bg-red-500/30 transition-colors shadow-md shadow-red-500/30 disabled:opacity-50"
        >
          {loadingCancel ? "Canceling..." : "Cancel Subscription"}
        </button>
      </motion.div>
    </motion.div>
  );
}

function InfoRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between items-center text-white/80 text-lg font-medium">
      <span>{label}</span>
      <span className="text-white">{value}</span>
    </div>
  );
}

const inputStyle =
  "w-full px-4 py-3 rounded-lg bg-black/20 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300";

const toastStyle = (type: "success" | "error") => ({
  borderRadius: "10px",
  background: "#1f1f1f",
  border: `1px solid ${type === "error" ? "#e53e3e" : "#6b46C1"}`,
  boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
  color: "#fff",
  padding: "12px 16px",
  fontSize: "0.95rem",
});
