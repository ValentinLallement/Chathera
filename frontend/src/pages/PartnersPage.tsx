import { useGetBots } from "../hooks/useApi";
import { motion } from "framer-motion";
import GirlIcon from "../assets/images/svgs/GirlPink.svg";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
};

export default function PartnersPage() {
  const bots = useGetBots();

  const handleCreateNew = () => {
    // TODO: Implement create new companion logic
    console.log("Create new companion clicked");
  };

  return (
    <div className="h-full w-full flex flex-col bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5">
      <div className="flex-1 flex flex-col p-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1 className="text-[#efefef] text-4xl font-bold font-poppins">
            My companions
          </h1>
          <p className="text-white/60 mt-2">
            Connect with your AI companions and start meaningful conversations
          </p>
        </motion.div>

        {bots.isLoading && (
          <div className="flex items-center justify-center flex-1">
            <div className="flex gap-2">
              <motion.div
                className="w-2 h-2 rounded-full bg-violet-400/60"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity, repeatDelay: 0.2 }}
              />
              <motion.div
                className="w-2 h-2 rounded-full bg-violet-400/60"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity, repeatDelay: 0.3 }}
              />
              <motion.div
                className="w-2 h-2 rounded-full bg-violet-400/60"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity, repeatDelay: 0.4 }}
              />
            </div>
          </div>
        )}

        {bots.isError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center flex-1 text-red-400"
          >
            Error: {bots.error.message}
          </motion.div>
        )}

        {bots.isSuccess && (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid gap-4"
          >
            {bots.data.map((bot) => (
              <motion.div
                key={bot.id}
                variants={itemVariants}
                className="group relative p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-violet-500/0 to-violet-500/0 group-hover:from-violet-500/5 group-hover:to-violet-500/0 transition-all duration-500 rounded-xl" />
                <div className="relative z-10 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-pink-500/10 flex items-center justify-center border border-pink-500/20">
                      <img
                        src={GirlIcon}
                        alt="Girl Icon"
                        className="w-5 h-5 text-pink-400 filter-pink-400"
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
      </div>
    </div>
  );
}
