import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";
import { changePassword } from "../api/api";
import { useAuthStore } from "../stores/authStore";
import {
  useGetSubscriptionInfos,
  useOpenCustomerPortal,
  useCancelSubscription,
} from "../hooks/useApi";
import { ChevronDown, ChevronUp } from "lucide-react";
import axios from "axios";

export default function SettingsPage() {
  const { accessToken } = useAuthStore();

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const {
    data: subscriptionData,
    isLoading,
    error,
  } = useGetSubscriptionInfos();

  const [newMessageLimit, setNewMessageLimit] = useState("");
  const [isUpdatingLimit, setIsUpdatingLimit] = useState(false);

  // Nouveaux hooks mutation
  const openCustomerPortal = useOpenCustomerPortal();
  const cancelSubscription = useCancelSubscription();

  const handleUpdateMessageLimit = async () => {
    setIsUpdatingLimit(true);
    try {
      await axios.put(
        "https://api.chathera.com/api/user/subscription/update",
        {
          message_limit:
            newMessageLimit === "" ? null : Number(newMessageLimit),
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      toast.success("Message limit successfully updated!", {
        style: toastStyle("success"),
      });
      setNewMessageLimit("");
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Failed to update limit", {
        style: toastStyle("error"),
      });
    } finally {
      setIsUpdatingLimit(false);
    }
  };

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
      toast.error("Password must be at least 8 characters long", {
        style: toastStyle("error"),
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
        style: toastStyle("success"),
      });

      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setShowPasswordForm(false);
    } catch (error: any) {
      toast.error(error.message || "An error occurred", {
        style: toastStyle("error"),
      });
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
    <div className="h-full w-full flex flex-col lg:flex-row bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5 overflow-scroll no-scrollbar">
      {/* Left column: settings - Make it more responsive */}
      <div className="flex-1 flex flex-col p-4 md:p-6 lg:p-8 space-y-6 md:space-y-8 w-full lg:max-w-2xl xl:max-w-3xl">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
            Settings
          </h1>
          <p className="text-gray-400">
            Manage your account settings and preferences
          </p>
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
      <div className="flex-1 p-4 md:p-6 lg:p-8 w-full">
        <SubscriptionInfoCard
          data={subscriptionData}
          loading={isLoading}
          error={error}
          onChangeInfoClick={handleChangeInfoClick}
          onCancelClick={handleCancelClick}
          loadingChangeInfo={openCustomerPortal.status === "pending"}
          loadingCancel={cancelSubscription.status === "pending"}
          newMessageLimit={newMessageLimit}
          setNewMessageLimit={setNewMessageLimit}
          isUpdatingLimit={isUpdatingLimit}
          setIsUpdatingLimit={setIsUpdatingLimit}
          handleUpdateMessageLimit={handleUpdateMessageLimit}
          accessToken={accessToken}
        />
      </div>
    </div>
  );
}

function InputField({ id, label, value, onChange, disabled }: any) {
  return (
    <div>
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-400 mb-1"
      >
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
  newMessageLimit,
  setNewMessageLimit,
  isUpdatingLimit,
  setIsUpdatingLimit,
  handleUpdateMessageLimit,
  accessToken,
}: any) {
  if (loading) return <p className="text-gray-400">Loading subscription...</p>;
  if (error || !data?.subscriptions)
    return <p className="text-red-500">Error loading subscription</p>;

  const sub = data.subscriptions;

  const plan = sub?.plan ?? "Unknown";
  const status = sub?.status ?? "Unknown";
  const messageLimit = sub?.message_limit ?? "∞";
  const remaining = sub?.remaining ?? "∞";
  const startDate = sub?.stripe_current_period_start
    ? new Date(sub.stripe_current_period_start).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "N/A";

  const endDate = sub?.stripe_current_period_end
    ? new Date(sub.stripe_current_period_end).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "N/A";

  const isPayg = plan === "payg";
  const botCount = sub?.bot_count ?? 0;
  const messageCount = sub?.message_count ?? 0;

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

      <motion.div className="space-y-6 relative z-10">
        <InfoRow label="Plan" value={plan} />
        <InfoRow label="Status" value={status} />
        <InfoRow label="Remaining Messages" value={remaining} />
        <InfoRow label="Period Start" value={startDate} />
        <InfoRow label="Period End" value={endDate} />
        <InfoRow
          label="Renewal Price"
          value={`${sub?.stripe_plan_amount_eur ?? "?"} ${
            sub?.stripe_currency?.toUpperCase() ?? "EUR"
          }`}
        />
        {isPayg && (
          <>
            <div className="flex items-center justify-between group relative">
              <span className="text-gray-300">Message Limit</span>
              <div className="flex items-center space-x-2">
                <span className="text-white">{messageLimit}</span>

                {/* Croix visible seulement si une limite est définie */}
                {messageLimit !== "∞" &&
                  messageLimit !== null &&
                  messageLimit !== undefined && (
                    <button
                      onClick={async () => {
                        setNewMessageLimit("");
                        setIsUpdatingLimit(true);
                        try {
                          await axios.put(
                            "https://api.chathera.com/api/user/subscription/update",
                            { message_limit: null },
                            {
                              headers: {
                                Authorization: `Bearer ${accessToken}`,
                              },
                            }
                          );
                          toast.success("Message limit cleared!", {
                            style: toastStyle("success"),
                          });
                        } catch (error: any) {
                          toast.error(
                            error?.response?.data?.detail ||
                              "Failed to clear limit",
                            {
                              style: toastStyle("error"),
                            }
                          );
                        } finally {
                          setIsUpdatingLimit(false);
                        }
                      }}
                      type="button"
                      aria-label="Clear message limit"
                      className="text-white/50 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                    >
                      ✕
                    </button>
                  )}
              </div>
            </div>

            <div className="mt-6 space-y-3">
              <label className="block text-sm font-medium text-gray-300"></label>

              <div className="relative">
                <input
                  type="number"
                  placeholder="Enter new limit"
                  value={newMessageLimit}
                  onChange={(e) => setNewMessageLimit(e.target.value)}
                  className="w-full pr-10 px-4 py-2 rounded-lg bg-black/20 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300"
                  disabled={isUpdatingLimit}
                />

                {/* Bouton croix visible uniquement si input non vide */}
                {newMessageLimit !== "" && (
                  <button
                    onClick={() => setNewMessageLimit("")}
                    type="button"
                    aria-label="Clear input"
                    className="
                      absolute 
                      top-1/2 
                      right-3 
                      -translate-y-1/2 
                      text-white/80 
                      hover:text-red-400 
                      transition-colors 
                      cursor-pointer
                      z-10
                      select-none
                    "
                  >
                    ✕
                  </button>
                )}
              </div>

              <button
                onClick={handleUpdateMessageLimit}
                disabled={isUpdatingLimit}
                className="w-full px-4 py-2 rounded-lg bg-violet-500/20 text-violet-300 font-medium border border-violet-500/20 hover:bg-violet-500/30 transition-colors disabled:opacity-50"
              >
                {isUpdatingLimit ? "Updating..." : "Update Limit"}
              </button>
            </div>
          </>
        )}
      </motion.div>

      {isPayg && (
        <motion.div
          className="mt-10 p-6 rounded-xl bg-black/30 border border-white/10 backdrop-blur-md shadow-inner text-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-xl font-bold mb-4 text-center text-violet-300">
            Usage (Pay-As-You-Go)
          </h3>
          <InfoRow
            label="Messages Sent"
            value={`${messageCount} × 0.01€ = ${(messageCount * 0.01).toFixed(
              2
            )}€`}
          />
          <InfoRow
            label="Bots Created"
            value={`${botCount} × 1€ = ${(botCount * 1).toFixed(2)}€`}
          />
          <div className="border-t border-white/10 my-4" />
          <InfoRow
            label="Estimated Total"
            value={`${(messageCount * 0.01 + botCount * 1).toFixed(2)} €`}
          />
        </motion.div>
      )}

      <motion.div
        className="mt-12 flex justify-center gap-6 relative z-10"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
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
