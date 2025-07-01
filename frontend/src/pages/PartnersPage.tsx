import { Link, useNavigate } from "react-router-dom";
import { useCreateBot, useGetBots, useRefreshToken } from "../hooks/useApi";
import { motion, AnimatePresence } from "framer-motion";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMars } from "@fortawesome/free-solid-svg-icons";
import { faVenus } from "@fortawesome/free-solid-svg-icons";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useSidebarStore } from "../stores/sidebarStore";
import { useConversationStore } from "../stores/conversationStore";
import { useAuthStore } from "../stores/authStore";

type Gender = "Male" | "Female";
type Personality = "Friendly" | "Professional" | "Casual" | "Serious" | "Sweet";

interface CompanionForm {
  gender: Gender | null;
  name: string;
  personality: Personality | null;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.25, 0.1, 0.25, 1] as [number, number, number, number],
    },
  },
};

const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? "100%" : "-100%",
    opacity: 0,
    scale: 0.99,
  }),
  center: {
    zIndex: 1,
    x: 0,
    opacity: 1,
    scale: 1,
  },
  exit: (direction: number) => ({
    zIndex: 0,
    x: direction < 0 ? "100%" : "-100%",
    opacity: 0,
    scale: 0.99,
  }),
};

const transition = {
  x: {
    type: "spring" as const,
    stiffness: 150,
    damping: 25,
    mass: 0.5,
    restDelta: 0.001,
  },
  opacity: {
    duration: 0.25,
    ease: "easeInOut" as const,
  },
  scale: {
    duration: 0.4,
    ease: "easeOut" as const,
  },
};

const stepVariants = {
  enter: {
    x: 50,
    opacity: 0,
  },
  center: {
    x: 0,
    opacity: 1,
  },
  exit: {
    x: -50,
    opacity: 0,
  },
};

const GenderStep = ({
  formData,
  setFormData,
  onNext,
}: {
  formData: CompanionForm;
  setFormData: (data: CompanionForm) => void;
  onNext: () => void;
}) => (
  <motion.div
    variants={stepVariants}
    initial="enter"
    animate="center"
    exit="exit"
    transition={{ duration: 0.2 }}
    className="space-y-6"
  >
    <div className="grid grid-cols-2 gap-4">
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          setFormData({ ...formData, gender: "Male" });
          onNext();
        }}
        className={`p-6 rounded-xl ${
          formData.gender === "Male"
            ? "bg-violet-500/20 border-violet-500/40"
            : "bg-white/5 border-white/10 hover:border-white/20"
        } backdrop-blur-sm border transition-all duration-200 cursor-pointer`}
      >
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 rounded-full bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
            <FontAwesomeIcon icon={faMars} size="xl" className="text-blue-50" />
          </div>
          <span className="text-white font-medium">Male</span>
        </div>
      </motion.button>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          setFormData({ ...formData, gender: "Female" });
          onNext();
        }}
        className={`p-6 rounded-xl ${
          formData.gender === "Female"
            ? "bg-violet-500/20 border-violet-500/40"
            : "bg-white/5 border-white/10 hover:border-white/20"
        } backdrop-blur-sm border transition-all duration-200 cursor-pointer`}
      >
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 rounded-full bg-pink-500/10 flex items-center justify-center border border-pink-500/20">
            <FontAwesomeIcon
              icon={faVenus}
              size="xl"
              className="text-blue-50"
            />
          </div>
          <span className="text-white font-medium">Female</span>
        </div>
      </motion.button>
    </div>
  </motion.div>
);

const NameStep = ({
  formData,
  setFormData,
  onNext,
}: {
  formData: CompanionForm;
  setFormData: (data: CompanionForm) => void;
  onNext: () => void;
}) => (
  <motion.div
    variants={stepVariants}
    initial="enter"
    animate="center"
    exit="exit"
    transition={{ duration: 0.2 }}
    className="space-y-6"
  >
    <div className="space-y-4">
      <input
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="Enter companion name..."
        className="w-full p-4 rounded-xl bg-white/5 border border-white/10 focus:border-violet-500/40 text-white placeholder-white/40 outline-none transition-all duration-200"
      />
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onNext}
        disabled={!formData.name.trim()}
        className="w-full px-6 py-4 rounded-xl bg-violet-500 hover:bg-violet-600 disabled:bg-violet-500/50 disabled:cursor-not-allowed text-white font-medium transition-all duration-200"
      >
        Continue
      </motion.button>
    </div>
  </motion.div>
);

const PersonalityStep = ({
  formData,
  setFormData,
  onNext,
}: {
  formData: CompanionForm;
  setFormData: (data: CompanionForm) => void;
  onNext: () => void;
}) => {
  const personalities: {
    type: Personality;
    icon: string;
    colorClasses: {
      button: string;
      icon: string;
    };
    description: string;
  }[] = [
    {
      type: "Friendly",
      icon: "😊",
      colorClasses: {
        button: "bg-violet-500/20 border-violet-500/40",
        icon: "bg-violet-500/10 border-violet-500/20",
      },
      description: "Warm and approachable",
    },
    {
      type: "Professional",
      icon: "👔",
      colorClasses: {
        button: "bg-blue-500/20 border-blue-500/40",
        icon: "bg-blue-500/10 border-blue-500/20",
      },
      description: "Focused and efficient",
    },
    {
      type: "Casual",
      icon: "😎",
      colorClasses: {
        button: "bg-green-500/20 border-green-500/40",
        icon: "bg-green-500/10 border-green-500/20",
      },
      description: "Laid-back and easy-going",
    },
    {
      type: "Serious",
      icon: "🤔",
      colorClasses: {
        button: "bg-gray-500/20 border-gray-500/40",
        icon: "bg-gray-500/10 border-gray-500/20",
      },
      description: "Direct and focused",
    },
    {
      type: "Sweet",
      icon: "🥰",
      colorClasses: {
        button: "bg-amber-500/20 border-amber-500/40",
        icon: "bg-amber-500/10 border-amber-500/20",
      },
      description: "Caring and empathetic",
    },
  ];

  return (
    <motion.div
      variants={stepVariants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.2 }}
      className="space-y-4"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {personalities.map(({ type, icon, colorClasses, description }) => (
          <motion.button
            key={type}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              setFormData({ ...formData, personality: type });
              onNext();
            }}
            className={`p-6 rounded-xl ${
              formData.personality === type
                ? colorClasses.button
                : "bg-white/5 border-white/10 hover:border-white/20"
            } backdrop-blur-sm border transition-all duration-200`}
          >
            <div className="flex items-center gap-4">
              <div
                className={`h-12 w-12 rounded-full ${colorClasses.icon} flex items-center justify-center border`}
              >
                <p className="text-2xl">{icon}</p>
              </div>
              <div className="text-left">
                <div className="text-white font-medium">{type}</div>
                <div className="text-white/60 text-sm">{description}</div>
              </div>
            </div>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

const LoadingStep = ({
  formData,
  setFormData,
  setCurrentStep,
  handleBackToList,
  bots,
}: {
  formData: CompanionForm;
  setFormData: (data: CompanionForm) => void;
  setCurrentStep: (step: number) => void;
  handleBackToList: () => void;
  bots: any;
}) => {
  const createBotMutation = useCreateBot();
  const { mutate: refreshToken } = useRefreshToken();
  const [hasRetried, setHasRetried] = useState(false);

  useEffect(() => {
    const createBot = async () => {
      try {
        await createBotMutation.mutateAsync({
          name: formData.name,
          gender: formData.gender!,
          personality: formData.personality!,
        });

        toast.success("Companion created successfully!", {
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

        setCurrentStep(1);
        setFormData({
          gender: null,
          name: "",
          personality: null,
        });
        handleBackToList();
        bots.refetch();
      } catch (error: any) {
        console.log("Error creating bot:", error);

        if (error.message.includes("403") && !hasRetried) {
          setHasRetried(true);
          await refreshToken(undefined, {
            onSuccess: () => createBot(),
          });
        } else if (error.message.includes("403")) {
          toast(
            (t) => (
              <div className="flex flex-col gap-2">
                <span>
                  Bot limit reached. Please upgrade your plan to create more
                  companions.
                </span>
                <Link
                  to="/pricing"
                  className="text-violet-400 hover:text-violet-300 underline transition-colors duration-200"
                  onClick={() => toast.dismiss(t.id)}
                >
                  Click here to upgrade
                </Link>
              </div>
            ),
            {
              style: {
                borderRadius: "10px",
                background: "#1f1f1f",
                border: "1px solid #e53e3e",
                boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
                color: "#fff",
                padding: "12px 16px",
                fontSize: "0.95rem",
              },
              duration: 5000,
            }
          );
          handleBackToList();
        } else {
          toast(
            (t) => (
              <div className="flex flex-col gap-2">
                <span>
                  Bot limit reached. Please{" "}
                  <a
                    href="/pricing"
                    className="text-blue-400 hover:text-blue-300 underline transition-colors duration-200"
                    onClick={() => toast.dismiss(t.id)}
                  >
                    upgrade
                  </a>{" "}
                  your plan to create more companions.
                </span>
              </div>
            ),
            {
              style: {
                borderRadius: "10px",
                background: "#1f1f1f",
                border: "1px solid #e53e3e",
                boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
                color: "#fff",
                padding: "12px 16px",
                fontSize: "0.95rem",
              },
              duration: 5000,
            }
          );
          setCurrentStep(1);
          setFormData({
            gender: null,
            name: "",
            personality: null,
          });
          handleBackToList();
        }
      }
    };

    createBot();
  }, []);

  return (
    <motion.div
      variants={stepVariants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.2 }}
      className="flex flex-col items-center justify-center gap-6 py-12"
    >
      <motion.div
        className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
      <p className="text-white/60">
        {createBotMutation.isError
          ? "Failed to create companion..."
          : "Creating your companion..."}
      </p>
    </motion.div>
  );
};

export default function PartnersPage() {
  const { user } = useAuthStore();
  const bots = useGetBots();
  const { mutate: refreshToken } = useRefreshToken();
  const [[isCreating, direction], setIsCreating] = useState([false, 0]);
  const [currentStep, setCurrentStep] = useState(1);
  const { isOpen } = useSidebarStore();
  const navigate = useNavigate();
  const { setSelectedBotId } = useConversationStore();
  const [formData, setFormData] = useState<CompanionForm>({
    gender: null,
    name: "",
    personality: null,
  });

  useEffect(() => {
    if (!user) {
      navigate("/login");
    }
  }, [user, navigate]);

  useEffect(() => {
    if (bots.isError) {
      console.error("Error fetching bots:", bots.error);
      refreshToken(undefined, {
        onSuccess: () => {
          bots.refetch();
        },
      });
    }
  }, [bots.isError]);

  const handleCreateNew = () => {
    setIsCreating([true, 1]);
  };

  const handleBackToList = () => {
    setIsCreating([false, -1]);
  };

  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    } else {
      handleBackToList();
    }
  };

  const handleBotClick = (botId: string) => {
    setSelectedBotId(botId);
    navigate("/dashboard/chat");
  };

  if (!user) {
    return null; // Return null while redirecting
  }

  return (
    <div className="h-full w-full flex flex-col bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5 scroll-auto">
      <div className="flex-1 flex flex-col p-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className={`mb-8 transition-all duration-300 ease-in-out ${
            isOpen ? "ml-0" : "ml-14 mt-[-10px]"
          }`}
        >
          <h1 className="text-[#efefef] text-4xl font-bold font-poppins">
            {isCreating ? "Create a companion" : "My companions"}
          </h1>
          <p className="text-white/60 mt-2">
            {isCreating
              ? "Create your perfect AI companion"
              : "Connect with your AI companions and start meaningful conversations"}
          </p>
        </motion.div>

        <div className="relative flex-1 h-fit scroll-smooth overflow-y-auto no-scrollbar">
          <AnimatePresence initial={false} custom={direction}>
            {!isCreating && (
              <motion.div
                key="list"
                custom={direction}
                variants={slideVariants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={transition}
                className="w-full absolute inset-0"
              >
                {/* Loading state */}
                {bots.isLoading && (
                  <div className="flex items-center justify-center flex-1">
                    <div className="flex gap-2">
                      <motion.div
                        className="w-2 h-2 rounded-full bg-violet-400/60"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          repeatDelay: 0.2,
                        }}
                      />
                      <motion.div
                        className="w-2 h-2 rounded-full bg-violet-400/60"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          repeatDelay: 0.3,
                        }}
                      />
                      <motion.div
                        className="w-2 h-2 rounded-full bg-violet-400/60"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          repeatDelay: 0.4,
                        }}
                      />
                    </div>
                  </div>
                )}

                {/* Error state */}
                {bots.isError && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center justify-center flex-1 text-red-400"
                  >
                    Error: {bots.error.message}
                  </motion.div>
                )}

                {/* Bots list */}
                {bots.isSuccess && (
                  <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    className="grid gap-4 scroll-smooth"
                  >
                    {bots.data.map((bot) => (
                      <motion.div
                        key={bot.bot_id}
                        variants={itemVariants}
                        onClick={() => handleBotClick(bot.bot_id)}
                        className="group relative p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-violet-500/0 to-violet-500/0 group-hover:from-violet-500/5 group-hover:to-violet-500/0 transition-all duration-500 rounded-xl" />
                        <div className="relative z-10 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div
                              className={`h-8 w-8 rounded-full ${
                                bot.gender == "Female"
                                  ? "bg-pink-500/10 border-pink-500/20"
                                  : "bg-blue-500/10 border-blue-500/20"
                              } flex items-center justify-center border`}
                            >
                              <FontAwesomeIcon
                                icon={bot.gender == "Female" ? faVenus : faMars}
                                size="lg"
                                className={
                                  bot.gender == "Female"
                                    ? "text-pink-400 filter-pink-400"
                                    : "text-blue-400 filter-blue-400"
                                }
                              />
                            </div>
                            <div>
                              <div className="flex items-center gap-3 mb-1">
                                <h3 className="text-white text-lg font-medium">
                                  {bot.name}
                                </h3>
                                <span className="inline-block px-3 py-0.5 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/10">
                                  Free companion
                                </span>
                              </div>
                              <p className="text-white/60 text-sm">
                                Click to start chatting
                              </p>
                            </div>
                          </div>
                          <div className="h-10 w-10 rounded-full bg-violet-500/10 flex items-center justify-center border border-violet-500/20 group-hover:bg-violet-500/20 transition-all duration-300">
                            <svg
                              className="w-5 h-5 text-violet-400"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                              />
                            </svg>
                          </div>
                        </div>
                      </motion.div>
                    ))}

                    {/* Create New Companion Card */}
                    <motion.div
                      variants={itemVariants}
                      onClick={handleCreateNew}
                      className="group relative p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-dashed border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/0 to-emerald-500/0 group-hover:from-emerald-500/5 group-hover:to-emerald-500/0 transition-all duration-500 rounded-xl" />
                      <div className="relative z-10 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                            <svg
                              className="w-5 h-5 text-emerald-400"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 4v16m8-8H4"
                              />
                            </svg>
                          </div>
                          <div>
                            <div className="flex items-center gap-3 mb-1">
                              <h3 className="text-white text-lg font-medium">
                                Create New Companion
                              </h3>
                              <span className="inline-block px-3 py-0.5 rounded-full text-xs font-medium bg-violet-500/20 text-violet-400 border border-violet-500/20">
                                Premium companion
                              </span>
                            </div>
                            <p className="text-white/60 text-sm">
                              Add a new AI companion
                            </p>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  </motion.div>
                )}
              </motion.div>
            )}

            {isCreating && (
              <motion.div
                key="creation"
                custom={direction}
                variants={slideVariants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={transition}
                className="w-full absolute inset-0"
              >
                <div className="flex flex-col gap-6">
                  <button
                    onClick={prevStep}
                    className="cursor-pointer self-start px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/60 hover:text-white/80 transition-all duration-200"
                  >
                    {currentStep === 1 ? "Back to companions" : "Back"}
                  </button>

                  <motion.div
                    variants={itemVariants}
                    className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10"
                  >
                    <div className="space-y-8">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {[1, 2, 3, 4].map((step) => (
                            <motion.div
                              key={step}
                              className={`h-2 rounded-full ${
                                step === currentStep
                                  ? "w-8 bg-violet-500"
                                  : step < currentStep
                                  ? "w-8 bg-violet-500/40"
                                  : "w-2 bg-white/20"
                              }`}
                              animate={
                                step === currentStep
                                  ? { scale: [1, 1.1, 1] }
                                  : {}
                              }
                              transition={{ duration: 0.5, repeat: Infinity }}
                            />
                          ))}
                        </div>
                        <div className="text-white/40 text-sm">
                          Step {currentStep} of 4
                        </div>
                      </div>

                      <AnimatePresence mode="wait">
                        {currentStep === 1 && (
                          <GenderStep
                            key="gender"
                            formData={formData}
                            setFormData={setFormData}
                            onNext={nextStep}
                          />
                        )}
                        {currentStep === 2 && (
                          <NameStep
                            key="name"
                            formData={formData}
                            setFormData={setFormData}
                            onNext={nextStep}
                          />
                        )}
                        {currentStep === 3 && (
                          <PersonalityStep
                            key="personality"
                            formData={formData}
                            setFormData={setFormData}
                            onNext={nextStep}
                          />
                        )}
                        {currentStep === 4 && (
                          <LoadingStep
                            key="loading"
                            formData={formData}
                            setFormData={setFormData}
                            setCurrentStep={setCurrentStep}
                            handleBackToList={handleBackToList}
                            bots={bots}
                          />
                        )}
                      </AnimatePresence>
                    </div>
                  </motion.div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
