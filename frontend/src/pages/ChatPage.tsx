import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faMars,
  faVenus,
  faChevronDown,
  faPlus,
  faPaperPlane,
} from "@fortawesome/free-solid-svg-icons";
import { useState, useEffect, useRef } from "react";
import {
  useGetBots,
  useGetConversations,
  useGetMessagesInConversation,
} from "../hooks/useApi";
import { useConversationStore } from "../stores/conversationStore";
import { useSidebarStore } from "../stores/sidebarStore";

export default function ChatPage() {
  const [isDropDownOpen, setIsDropDownOpen] = useState(false);
  const { isOpen } = useSidebarStore();
  const [message, setMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const bots = useGetBots();
  const conversations = useGetConversations();
  const { selectedBotId, setSelectedBotId } = useConversationStore();

  // Find the current conversation for the selected bot
  const currentConversation = conversations.data?.find(
    (conv) => conv.bot_id === selectedBotId
  );

  // Fetch messages for the current conversation
  const messagesQuery = useGetMessagesInConversation(
    currentConversation?.id || ""
  );

  const selectedBot = bots.data?.find((bot) => bot.bot_id === selectedBotId);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (bots.data && bots.data.length > 0 && !selectedBotId) {
      setSelectedBotId(bots.data[0].bot_id);
    }
  }, [bots.data, selectedBotId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messagesQuery.data]);

  // Refetch messages when conversation changes
  useEffect(() => {
    if (currentConversation?.id) {
      messagesQuery.refetch();
    }
  }, [currentConversation?.id]);

  return (
    <div className="h-full w-full flex flex-col bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5">
      <div className="flex-1 flex flex-col overflow-y-auto no-scrollbar">
        {/* Dropdown header */}
        <div className="relative p-4 border-b border-white/5">
          <button
            onClick={() => setIsDropDownOpen(!isDropDownOpen)}
            className={`min-w-[200px] w-[20%] flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 ease-in-out ${
              isOpen ? "border border-white/10" : "ml-16"
            }`}
          >
            <div className="flex items-center gap-3">
              {selectedBot && (
                <>
                  <div
                    className={`h-8 w-8 rounded-full ${
                      selectedBot.gender === "Female"
                        ? "bg-pink-500/10 border-pink-500/20"
                        : "bg-blue-500/10 border-blue-500/20"
                    } flex items-center justify-center border`}
                  >
                    <FontAwesomeIcon
                      icon={selectedBot.gender === "Female" ? faVenus : faMars}
                      className={
                        selectedBot.gender === "Female"
                          ? "text-pink-400"
                          : "text-blue-400"
                      }
                    />
                  </div>
                  <span className="text-white font-medium">
                    {selectedBot.name}
                  </span>
                </>
              )}
            </div>
            <motion.div
              animate={{ rotate: isDropDownOpen ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <FontAwesomeIcon icon={faChevronDown} className="text-white/60" />
            </motion.div>
          </button>

          <AnimatePresence>
            {isDropDownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="absolute top-full left-0 right-0 mt-2 mx-4 p-2 rounded-xl bg-[#0A0A0A] border border-white/10 shadow-xl z-50"
              >
                <div className="space-y-1">
                  {bots.data?.map((bot) => (
                    <button
                      key={bot.bot_id}
                      onClick={() => {
                        setSelectedBotId(bot.bot_id);
                        setIsDropDownOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                        selectedBotId === bot.bot_id
                          ? "bg-violet-500/20"
                          : "hover:bg-white/5"
                      }`}
                    >
                      <div
                        className={`h-8 w-8 rounded-full ${
                          bot.gender === "Female"
                            ? "bg-pink-500/10 border-pink-500/20"
                            : "bg-blue-500/10 border-blue-500/20"
                        } flex items-center justify-center border`}
                      >
                        <FontAwesomeIcon
                          icon={bot.gender === "Female" ? faVenus : faMars}
                          className={
                            bot.gender === "Female"
                              ? "text-pink-400"
                              : "text-blue-400"
                          }
                        />
                      </div>
                      <span className="text-white font-medium">{bot.name}</span>
                    </button>
                  ))}

                  {/* Create new companion button */}
                  <button
                    onClick={() => {
                      navigate("/dashboard/partners");
                      setIsDropDownOpen(false);
                    }}
                    className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors border-t border-white/5"
                  >
                    <div className="h-8 w-8 rounded-full bg-emerald-500/10 border-emerald-500/20 flex items-center justify-center border">
                      <FontAwesomeIcon
                        icon={faPlus}
                        className="text-emerald-400"
                      />
                    </div>
                    <span className="text-white font-medium">
                      Create New Companion
                    </span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Chat content area */}
        <div className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-4">
          {messagesQuery.data?.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.user_id === selectedBotId ? "justify-start" : "justify-end"
              }`}
            >
              <div
                className={`max-w-[70%] p-3 rounded-xl ${
                  msg.user_id === selectedBotId
                    ? "bg-white/5 text-white"
                    : "bg-violet-500/20 text-white"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Message input */}
        <form onSubmit={() => {}} className="p-4 border-t border-white/5">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-white/5 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-violet-500/50 transition-all"
            />
            <button
              type="submit"
              disabled={!message.trim() || !currentConversation?.id}
              className="p-3 rounded-xl bg-violet-500 hover:bg-violet-600 disabled:opacity-50 disabled:hover:bg-violet-500 transition-colors"
            >
              <FontAwesomeIcon icon={faPaperPlane} className="text-white" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
