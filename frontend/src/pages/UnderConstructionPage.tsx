import { motion } from "framer-motion";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCog } from "@fortawesome/free-solid-svg-icons";
import Title from "../components/Title";

export default function UnderConstructionPage() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-b from-gray-900 to-black">
      <Title>Under Construction - Chathera</Title>
      <div className="relative flex flex-col items-center gap-8 p-8 max-w-3xl mx-auto text-center">
        {/* Background gradient effects */}
        <div className="absolute inset-0 bg-gradient-to-r from-violet-500/5 via-pink-500/5 to-violet-500/5 rounded-3xl blur-3xl" />
        <div className="absolute -top-[25%] -left-[25%] w-[150%] h-[150%] bg-gradient-conic from-violet-500/10 via-transparent to-transparent opacity-20 animate-slow-spin" />

        {/* Icon animation */}
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{
            type: "spring",
            stiffness: 260,
            damping: 20,
          }}
          className="relative"
        >
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-violet-500/10 to-pink-500/10 flex items-center justify-center border border-violet-500/20">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: "linear",
              }}
              className="relative"
            >
              <FontAwesomeIcon
                icon={faCog}
                className="text-5xl text-violet-400"
              />
            </motion.div>
          </div>

          {/* Small floating cogs */}
          <motion.div
            className="absolute -top-4 -right-4"
            animate={{ rotate: -360 }}
            transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
          >
            <FontAwesomeIcon
              icon={faCog}
              className="text-2xl text-pink-400/60"
            />
          </motion.div>
          <motion.div
            className="absolute -bottom-2 -left-4"
            animate={{ rotate: -360 }}
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          >
            <FontAwesomeIcon
              icon={faCog}
              className="text-lg text-violet-400/60"
            />
          </motion.div>
        </motion.div>

        {/* Text content */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="relative space-y-4"
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-violet-400 to-pink-400">
            Under Construction
          </h1>
          <p className="text-lg text-white/60 max-w-md mx-auto">
            This page is currently under construction but will be available
            soon! Stay tuned for exciting new features.
          </p>
        </motion.div>

        {/* Status badges */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="flex flex-wrap justify-center gap-3"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-violet-500/20 text-violet-400 border border-violet-500/20">
            Coming Soon
          </span>
          <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-pink-500/20 text-pink-400 border border-pink-500/20">
            Work in Progress
          </span>
          <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/20">
            Stay Tuned
          </span>
        </motion.div>
      </div>
    </div>
  );
}
