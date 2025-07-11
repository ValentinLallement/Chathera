import { motion } from "framer-motion";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { Link, useNavigate } from "react-router-dom";
import Title from "../components/Title";

export default function CancelPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-b from-gray-900 to-black">
      <Title>Payment Cancelled - Chathera</Title>
      <div className="relative flex flex-col items-center gap-8 p-8 max-w-3xl mx-auto text-center">
        {/* Background effects */}
        <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 via-orange-400/5 to-red-500/5 rounded-3xl blur-3xl" />
        <div className="absolute -top-[25%] -left-[25%] w-[150%] h-[150%] bg-gradient-conic from-red-500/10 via-transparent to-transparent opacity-20 animate-slow-spin" />

        {/* Cancel X mark animation */}
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
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-red-500/10 to-orange-400/10 flex items-center justify-center border border-red-500/20">
            <motion.div
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              transition={{
                delay: 0.2,
                type: "spring",
                stiffness: 200,
                damping: 20,
              }}
            >
              <FontAwesomeIcon
                icon={faTimes}
                className="text-5xl text-red-400"
              />
            </motion.div>
          </div>

          {/* Cancel particles */}
          <motion.div
            className="absolute -top-4 -right-4 w-8 h-8 rounded-full bg-red-500/20"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: [0, 1.2, 0], opacity: [0, 1, 0] }}
            transition={{
              delay: 0.3,
              duration: 1.5,
              repeat: Infinity,
              repeatDelay: 2,
            }}
          />
          <motion.div
            className="absolute -bottom-2 -left-4 w-6 h-6 rounded-full bg-orange-400/20"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: [0, 1.2, 0], opacity: [0, 1, 0] }}
            transition={{
              delay: 0.5,
              duration: 1.5,
              repeat: Infinity,
              repeatDelay: 2,
            }}
          />
        </motion.div>

        {/* Text content */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="relative space-y-4"
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-400 to-orange-500">
            Payment Cancelled
          </h1>
          <p className="text-lg text-white/60 max-w-md mx-auto">
            Your payment was cancelled. No charges were made to your account.
          </p>
        </motion.div>

        {/* Action buttons */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex gap-4 flex-wrap justify-center"
        >
          <button
            onClick={() => navigate("/pricing")}
            className="inline-block px-8 py-4 rounded-xl bg-gradient-to-r from-red-500 to-red-600 text-white font-medium hover:from-red-600 hover:to-red-700 transition-all duration-200 hover:scale-[1.02] hover:shadow-lg"
          >
            Try Again
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="inline-block px-8 py-4 rounded-xl bg-white/5 border border-white/10 text-white font-medium hover:bg-white/10 transition-all duration-200 hover:scale-[1.02] hover:shadow-lg"
          >
            Back to Dashboard
          </button>
        </motion.div>
      </div>
    </div>
  );
}
