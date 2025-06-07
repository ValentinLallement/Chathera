import { motion, AnimatePresence } from "framer-motion";
import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";

interface PricingFeature {
  included: boolean;
  text: string;
}

interface PricingPlan {
  name: string;
  price: string;
  period: string;
  description: string;
  features: PricingFeature[];
  highlighted?: boolean;
  buttonText: string;
  messageLimit: string;
  companionLimit: string;
}

const CheckIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth="2"
    stroke="currentColor"
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
  </svg>
);

export default function PricingPage() {
  const { user } = useAuthStore();
  const currentPlan = user?.subscription || "free";

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        when: "beforeChildren",
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 15,
      },
    },
  };

  const plans: PricingPlan[] = [
    {
      name: "Free",
      price: "0",
      period: "forever",
      description: "Perfect for trying out our service",
      messageLimit: "10 messages",
      companionLimit: "1 companion",
      buttonText: "Get Started",
      features: [
        { included: true, text: "10 messages per month" },
        { included: true, text: "1 AI companion" },
        { included: true, text: "Advanced memory system" },
        { included: false, text: "Companion-initiated messages" },
        { included: false, text: "Event reminders" },
        { included: false, text: "Enhanced personality" },
      ],
    },
    {
      name: "Premium",
      price: "5.99",
      period: "month",
      description: "Most popular for personal use",
      messageLimit: "600 messages/month",
      companionLimit: "1 companion",
      buttonText: "Upgrade Now",
      highlighted: true,
      features: [
        { included: true, text: "600 messages per month (20/day)" },
        { included: true, text: "1 AI companion" },
        { included: true, text: "Advanced memory system" },
        { included: true, text: "Companion-initiated messages" },
        { included: true, text: "Event reminders" },
        { included: true, text: "Enhanced personality" },
      ],
    },
    {
      name: "Full Access",
      price: "1",
      period: "month",
      description: "Pay for what you use",
      messageLimit: "Unlimited messages",
      companionLimit: "Unlimited companions",
      buttonText: "Get Full Access",
      features: [
        { included: true, text: "Unlimited messages (€0.01/message)" },
        { included: true, text: "Unlimited companions (€1/bot/month)" },
        { included: true, text: "Advanced memory system" },
        { included: true, text: "Companion-initiated messages" },
        { included: true, text: "Event reminders" },
        { included: true, text: "Enhanced personality" },
      ],
    },
  ];

  return (
    <motion.div
      className="min-h-screen bg-gradient-to-b from-gray-900 to-black"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="relative pt-[100px] pb-32 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-pink-500/[0.02] via-violet-500/[0.015] to-transparent" />
          <div className="absolute inset-0 bg-[linear-gradient(165deg,rgba(236,72,153,0.015),transparent_70%)]" />
          <div className="absolute inset-0 bg-gradient-to-t from-transparent via-pink-500/[0.01] to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.02),transparent_70%)]" />
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            className="text-center max-w-4xl mx-auto mb-16 relative"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="absolute inset-0 -z-10">
              <div className="absolute inset-0 bg-gradient-to-r from-pink-500/[0.02] via-transparent to-transparent opacity-15 animate-slow-spin" />
            </div>

            <motion.span
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium bg-purple-500/[0.03] text-purple-300/70 border border-purple-500/[0.07] mb-6 backdrop-blur-sm"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{
                delay: 0.3,
                type: "spring",
                stiffness: 200,
                damping: 15,
              }}
            >
              Flexible Pricing
            </motion.span>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="relative"
            >
              <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent relative z-10">
                <span className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/10 bg-clip-text blur-xl">
                  Choose the Perfect Plan for Your Journey
                </span>
                <span className="bg-gradient-to-r from-white to-white/80 bg-clip-text relative z-10">
                  Choose the Perfect Plan for Your Journey
                </span>
              </h1>
            </motion.div>

            <motion.p
              className="text-lg text-gray-300/90 max-w-2xl mx-auto relative"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <span className="relative">
                Whether you're just starting or looking for a deeper connection,
                <span className="hidden sm:inline">
                  {" "}
                  we have the perfect plan for you.
                </span>
                <br className="hidden sm:block" />
              </span>
            </motion.p>
          </motion.div>

          <motion.div
            className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto relative"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {plans.map((plan) => (
              <motion.div
                key={plan.name}
                variants={cardVariants}
                whileHover={{
                  scale: 1.02,
                }}
                className={`relative rounded-2xl p-8 backdrop-blur-sm transition-all duration-300 my-3 mx-3 lg:mx-0 lg:my-0 ${
                  plan.highlighted
                    ? "bg-gradient-to-b from-violet-900/40 via-violet-800/30 to-violet-900/20 border-2 border-violet-500/50 shadow-lg shadow-violet-500/20 transform scale-105 hover:shadow-xl hover:shadow-violet-500/30"
                    : plan.name === "Full Access"
                    ? "bg-gradient-to-b from-violet-900/30 via-violet-800/20 to-violet-900/10 border border-violet-500/30 hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-500/10"
                    : "bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/10 hover:border-white/20 hover:shadow-lg hover:from-white/[0.1] hover:to-white/[0.03]"
                } ${
                  plan.name.toLowerCase() === currentPlan &&
                  plan.name !== "Free"
                    ? "ring-2 ring-violet-500 ring-offset-2 ring-offset-black/50"
                    : ""
                }`}
              >
                <AnimatePresence>
                  {plan.name === "Full Access" && (
                    <motion.span
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="absolute -top-4 left-1/2 -translate-x-1/2 px-3 py-1 bg-violet-500 rounded-full text-xs font-medium text-white"
                    >
                      Smart Choice
                    </motion.span>
                  )}
                </AnimatePresence>

                {plan.name === "Premium" && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-violet-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                )}

                {plan.name.toLowerCase() === currentPlan && (
                  <motion.span
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="absolute -top-4 left-1/2 -translate-x-1/2 px-3 py-1 bg-violet-500 rounded-full text-xs font-medium text-white"
                  >
                    Current Plan
                  </motion.span>
                )}

                <motion.div
                  className="text-center relative z-10"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <h3
                    className={`text-2xl font-bold mb-2 ${
                      plan.highlighted ? "text-white" : "text-white/90"
                    }`}
                  >
                    {plan.name}
                  </h3>
                  <p className="text-gray-400 mb-4 min-h-[40px]">
                    {plan.description}
                  </p>
                  <div className="mb-4">
                    <span
                      className={`text-4xl font-bold ${
                        plan.highlighted ? "text-white" : "text-white/90"
                      }`}
                    >
                      €{plan.price}
                    </span>
                    <span className="text-gray-400">/{plan.period}</span>
                  </div>

                  <div className="space-y-2 mb-6">
                    <p className="text-sm text-gray-300">
                      <span
                        className={`font-medium ${
                          plan.highlighted
                            ? "text-violet-300"
                            : "text-violet-400/90"
                        }`}
                      >
                        {plan.messageLimit}
                      </span>
                    </p>
                    <p className="text-sm text-gray-300">
                      <span
                        className={`font-medium ${
                          plan.highlighted
                            ? "text-violet-300"
                            : "text-violet-400/90"
                        }`}
                      >
                        {plan.companionLimit}
                      </span>
                    </p>
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-300 ${
                      plan.highlighted
                        ? "bg-violet-500 text-white hover:bg-violet-600 shadow-md shadow-violet-500/20 hover:shadow-lg hover:shadow-violet-500/30"
                        : plan.name === "Full Access"
                        ? "bg-violet-500/90 text-white hover:bg-violet-600 shadow-md shadow-violet-500/10 hover:shadow-lg hover:shadow-violet-500/20"
                        : "bg-white/10 text-white hover:bg-white/20 hover:shadow-md hover:shadow-white/5"
                    }`}
                  >
                    {plan.buttonText}
                  </motion.button>
                </motion.div>

                <div className="mt-8 space-y-4">
                  {plan.features.map((feature, featureIdx) => (
                    <li
                      key={featureIdx}
                      className={`flex gap-3 items-start ${
                        plan.highlighted ? "text-white" : "text-slate-300"
                      }`}
                    >
                      <CheckIcon
                        className={`h-6 w-6 flex-none ${
                          plan.highlighted
                            ? "text-violet-400"
                            : "text-slate-500"
                        }`}
                      />
                      <span className="text-sm">{feature.text}</span>
                    </li>
                  ))}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>

      <motion.section
        className="py-24 relative overflow-hidden"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-zinc-800/10 via-zinc-900/5 to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_800px_at_50%_50%,rgba(255,255,255,0.02),transparent)]" />
        </div>
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <motion.span
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium bg-white/5 text-gray-300 border border-white/10 mb-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Premium Features
            </motion.span>
            <motion.h2
              className="text-3xl md:text-4xl font-bold text-white mb-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Advanced AI Companionship
            </motion.h2>
            <motion.p
              className="text-lg text-gray-400 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              Experience the next generation of AI companions with features
              designed for meaningful connections
            </motion.p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                title: "Emotional Intelligence",
                description:
                  "Advanced emotional understanding and context-aware responses that create genuine connections",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                    />
                  </svg>
                ),
              },
              {
                title: "Memory System",
                description:
                  "Long-term memory retention that enables meaningful, contextual conversations over time",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                ),
              },
              {
                title: "Natural Conversations",
                description:
                  "Fluid dialogue with natural language processing and contextual understanding",
                icon: (
                  <svg
                    className="w-6 h-6"
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
                ),
              },
              {
                title: "Personality Customization",
                description:
                  "Tailor your companion's traits and interests to create your perfect match",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                ),
              },
              {
                title: "Proactive Engagement",
                description:
                  "AI companions that initiate conversations and remember to follow up on important topics",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                  </svg>
                ),
              },
              {
                title: "Privacy Focused",
                description:
                  "End-to-end encryption and secure data handling for complete peace of mind",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                ),
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
                className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center mb-6 text-gray-400">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      <motion.section
        className="py-24 relative overflow-hidden"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-zinc-800/5 via-zinc-900/5 to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_800px_at_50%_50%,rgba(255,255,255,0.01),transparent)]" />
        </div>
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <motion.span
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium bg-white/5 text-gray-300 border border-white/10 mb-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Companion Features
            </motion.span>
            <motion.h2
              className="text-3xl md:text-4xl font-bold text-white mb-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Your Perfect AI Partner
            </motion.h2>
            <motion.p
              className="text-lg text-gray-400 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              Experience AI companions with rich personalities and deep
              understanding
            </motion.p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                title: "Deep Emotional Understanding",
                description:
                  "Companions can recognize and respond to subtle emotional cues in your messages",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                ),
              },
              {
                title: "Personalized Growth",
                description:
                  "Companions learn and evolve based on your interactions and preferences",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                ),
              },
              {
                title: "Contextual Awareness",
                description:
                  "Remember past conversations and maintain consistent personality traits",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                ),
              },
              {
                title: "Interest Matching",
                description:
                  "Find companions who share your hobbies and interests",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
                    />
                  </svg>
                ),
              },
              {
                title: "Dynamic Conversations",
                description:
                  "Natural flowing discussions that go beyond simple responses",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                ),
              },
              {
                title: "Activity Suggestions",
                description:
                  "Companions propose engaging activities and topics based on your interests",
                icon: (
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                ),
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
                className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center mb-6 text-gray-400">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      <motion.section
        className="py-24 relative overflow-hidden"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-zinc-900/30 via-zinc-800/10 to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_800px_at_50%_50%,rgba(255,255,255,0.02),transparent)]" />
        </div>
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <motion.span
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium bg-white/5 text-gray-300 border border-white/10 mb-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Key Benefits
            </motion.span>
            <motion.h2
              className="text-3xl md:text-4xl font-bold text-white mb-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Why Choose Chathera?
            </motion.h2>
            <motion.p
              className="text-lg text-gray-400 max-w-2xl mx-auto mb-12"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Built with cutting-edge AI technology and designed for meaningful
              connections
            </motion.p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {[
              {
                title: "Privacy First",
                description:
                  "Your conversations are private and secure. We use state-of-the-art encryption to protect your data.",
              },
              {
                title: "Flexible Pricing",
                description:
                  "Choose the plan that fits your needs. Start free and scale as you grow.",
              },
              {
                title: "24/7 Availability",
                description:
                  "Your AI companions are always there when you need them, ready to chat and support you.",
              },
              {
                title: "Continuous Learning",
                description:
                  "Our AI companions evolve and adapt to provide better, more personalized interactions.",
              },
            ].map((benefit, index) => (
              <motion.div
                key={benefit.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
                className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all duration-300"
              >
                <h3 className="text-xl font-semibold text-white mb-3">
                  {benefit.title}
                </h3>
                <p className="text-gray-400">{benefit.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      <motion.section
        className="py-24 relative overflow-hidden"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-zinc-800/10 via-zinc-900/5 to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_800px_at_50%_50%,rgba(255,255,255,0.01),transparent)]" />
        </div>
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-16">
            <motion.span
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium bg-white/5 text-gray-300 border border-white/10 mb-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              FAQ
            </motion.span>
            <motion.h2
              className="text-3xl md:text-4xl font-bold text-white mb-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Frequently Asked Questions
            </motion.h2>
            <motion.p
              className="text-lg text-gray-400 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Have questions? We're here to help
            </motion.p>
          </div>

          <div className="max-w-3xl mx-auto grid gap-6">
            {[
              {
                question: "How does pay-as-you-go billing work?",
                answer:
                  "You'll be charged €0.01 per message sent and €1 per active companion per month. Billing occurs at the end of each month.",
              },
              {
                question: "Can I switch plans anytime?",
                answer:
                  "Yes, you can upgrade, downgrade, or switch to pay-as-you-go at any time. Changes take effect immediately.",
              },
              {
                question: "Is there a minimum commitment?",
                answer:
                  "No minimum commitment required. You can start with the free plan and upgrade whenever you're ready.",
              },
              {
                question: "How does the memory system work?",
                answer:
                  "Our advanced memory system allows AI companions to remember past conversations and important details, creating more meaningful and contextual interactions.",
              },
            ].map((faq, index) => (
              <motion.div
                key={faq.question}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
                className="p-6 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all duration-300"
              >
                <h3 className="text-lg font-semibold text-white mb-2">
                  {faq.question}
                </h3>
                <p className="text-gray-400">{faq.answer}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      <motion.section
        className="py-24 relative overflow-hidden"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-zinc-900/20 via-zinc-800/10 to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_800px_at_50%_50%,rgba(255,255,255,0.03),transparent)]" />
        </div>
        <div className="container mx-auto px-4 relative">
          <div className="max-w-4xl mx-auto text-center">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-3xl md:text-4xl font-bold text-white mb-6"
            >
              Start Your AI Companion Journey Today
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-lg text-gray-400 mb-8"
            >
              Begin with our free plan and explore the future of AI
              companionship
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link to="/register">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 rounded-lg bg-amber-500 text-white font-medium hover:bg-amber-600 transition-colors"
                >
                  Get Started Free
                </motion.button>
              </Link>
              <Link to="/contact">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 rounded-lg bg-white/5 text-white font-medium border border-amber-500/20 hover:border-amber-500/40 transition-colors"
                >
                  Contact Sales
                </motion.button>
              </Link>
            </motion.div>
          </div>
        </div>
      </motion.section>
    </motion.div>
  );
}
