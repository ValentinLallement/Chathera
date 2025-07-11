import { motion } from "framer-motion";
import type { Variants } from "framer-motion";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faMessage,
  faHeart,
  faClock,
  faArrowRight,
  faCrown,
  faStar,
} from "@fortawesome/free-solid-svg-icons";
import { useNavigate } from "react-router-dom";
import { useSidebarStore } from "../stores/sidebarStore";
import { useStatsStore } from "../stores/statsStore";

const features = [
  {
    title: "Unlimited Conversations",
    description: "Chat without limits with all your companions",
    icon: faMessage,
  },
  {
    title: "Custom Personalities",
    description: "Create companions with unique traits and interests",
    icon: faStar,
  },
  {
    title: "Priority Support",
    description: "Get help when you need it, 24/7",
    icon: faCrown,
  },
];

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.43, 0.13, 0.23, 0.96],
    },
  },
};

export default function HomePage() {
  const navigate = useNavigate();
  const { isOpen } = useSidebarStore();
  const {
    conversations,
    remainingMessages,
    hotPicsLeft,
    longestStreak,
    updateAffection,
  } = useStatsStore();

  const handleConversationClick = (id: string) => {
    // Update affection when clicking on a conversation
    // This is just an example - you might want to track actual message counts
    const conversation = conversations.find((conv) => conv.id === id);
    if (conversation) {
      updateAffection(id, (conversation.messageCount || 0) + 1);
    }
    navigate(`/dashboard/chat/${id}`);
  };

  const getAffectionColor = (affection: number) => {
    if (affection >= 90)
      return "text-pink-400 bg-pink-500/10 border-pink-500/20";
    if (affection >= 70)
      return "text-violet-400 bg-violet-500/10 border-violet-500/20";
    return "text-purple-400 bg-purple-500/10 border-purple-500/20";
  };

  return (
    <div className="h-full w-full flex flex-col bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5">
      <motion.div
        className="flex-1 flex flex-col p-8 overflow-y-auto no-scrollbar"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Welcome Section */}
        <motion.div
          variants={itemVariants}
          className={`mb-8 transition-all duration-300 ease-in-out ${
            isOpen ? "ml-0" : "ml-14"
          }`}
        >
          <h1 className="text-[#efefef] text-4xl font-bold">Welcome back</h1>
          <p className="text-white/60 mt-2">
            Here's what's happening with your AI companions
          </p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          variants={itemVariants}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
        >
          <div className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-violet-500/10 flex items-center justify-center border border-violet-500/20">
              <FontAwesomeIcon icon={faMessage} className="text-violet-400" />
            </div>
            <div>
              <p className="text-white/60 text-sm">Remaining Messages</p>
              <p className="text-white text-xl font-bold">
                {remainingMessages}
              </p>
            </div>
          </div>

          <div className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-pink-500/10 flex items-center justify-center border border-pink-500/20">
              <FontAwesomeIcon icon={faHeart} className="text-pink-400" />
            </div>
            <div>
              <p className="text-white/60 text-sm">
                Remaining <i>HotPics</i> generations
              </p>
              <p className="text-white text-xl font-bold">{hotPicsLeft}</p>
            </div>
          </div>

          <div className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <FontAwesomeIcon icon={faClock} className="text-emerald-400" />
            </div>
            <div>
              <p className="text-white/60 text-sm">Longest Streak</p>
              <p className="text-white text-xl font-bold">
                {longestStreak} days
              </p>
            </div>
          </div>
        </motion.div>

        {/* Recent Conversations with Affection */}
        <motion.div variants={itemVariants} className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white text-xl font-bold">
              Recent Conversations
            </h2>
            <button
              onClick={() => navigate("/dashboard/partners")}
              className="text-violet-400 hover:text-violet-300 transition-colors text-sm flex items-center gap-2"
            >
              View all
              <FontAwesomeIcon icon={faArrowRight} className="text-sm" />
            </button>
          </div>

          <div className="space-y-4">
            {conversations.map((conversation) => (
              <motion.div
                key={conversation.id}
                onClick={() => handleConversationClick(conversation.id)}
                className="group p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer relative overflow-hidden"
                whileHover={{ scale: 1.01 }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-violet-500/0 to-violet-500/0 group-hover:from-violet-500/5 group-hover:to-violet-500/0 transition-all duration-500" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-white font-medium flex items-center gap-2">
                        {conversation.botName}
                        {conversation.unread && (
                          <span className="w-2 h-2 rounded-full bg-violet-500" />
                        )}
                      </h3>
                      <span className="text-white/40 text-sm">
                        {conversation.timestamp}
                      </span>
                    </div>
                    <div
                      className={`px-3 py-1 rounded-full border ${getAffectionColor(
                        conversation.affection
                      )} text-sm`}
                    >
                      <FontAwesomeIcon icon={faHeart} className="mr-2" />
                      {conversation.affection}%
                    </div>
                  </div>
                  <p className="text-white/60 text-sm mb-2 line-clamp-1">
                    {conversation.lastMessage}
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-white/40 text-xs">
                      {conversation.personality}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Upgrade Section */}
        <motion.div variants={itemVariants} className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white text-xl font-bold">Upgrade to Premium</h2>
            <div className="flex items-center gap-2">
              <FontAwesomeIcon icon={faCrown} className="text-yellow-400" />
              <span className="text-white/60 text-sm">Unlock all features</span>
            </div>
          </div>

          <div className="rounded-xl bg-gradient-to-br from-violet-500/10 via-pink-500/10 to-violet-500/10 backdrop-blur-sm border border-white/10 p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  className="p-4 rounded-lg bg-black/20 border border-white/5 flex flex-col items-center text-center gap-3"
                  whileHover={{ scale: 1.02 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="h-12 w-12 rounded-full bg-violet-500/10 flex items-center justify-center border border-violet-500/20">
                    <FontAwesomeIcon
                      icon={feature.icon}
                      className="text-violet-400"
                    />
                  </div>
                  <h3 className="text-white font-medium">{feature.title}</h3>
                  <p className="text-white/60 text-sm">{feature.description}</p>
                </motion.div>
              ))}
            </div>
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => navigate("/pricing")}
                className="px-6 py-3 rounded-lg bg-violet-500 hover:bg-violet-600 text-white font-medium transition-colors"
              >
                Upgrade Now
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
