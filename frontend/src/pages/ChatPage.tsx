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
import { useState, useEffect, useRef, useLayoutEffect } from "react";
import {
  useGetBots,
  useGetConversations,
  useGetMessagesInConversation,
  useRefreshToken,
} from "../hooks/useApi";
import { useConversationStore } from "../stores/conversationStore";
import { useSidebarStore } from "../stores/sidebarStore";
import { useAuthStore } from "../stores/authStore";
import toast from "react-hot-toast";

interface Message {
  id: string;
  content: string;
  user_id: string;
  conversation_id: string;
  created_at: string;
}

export default function ChatPage() {
  const [isDropDownOpen, setIsDropDownOpen] = useState(false);
  const { isOpen } = useSidebarStore();
  const [message, setMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const navigate = useNavigate();
  const { accessToken } = useAuthStore();
  const { mutateAsync: refreshToken } = useRefreshToken();
  const [hasRetried, setHasRetried] = useState(false);
  const bots = useGetBots();
  const conversations = useGetConversations();
  const { selectedBotId, setSelectedBotId } = useConversationStore();

  const currentConversation = conversations.data?.find(
    (conv) => conv.bot_id === selectedBotId
  );

  const messagesQuery = useGetMessagesInConversation(
    currentConversation?.id || ""
  );

  const selectedBot = bots.data?.find((bot) => bot.bot_id === selectedBotId);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const connectWebSocket = async (token: string) => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/chat?token=${token}`);
    websocketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connection established");
      setHasRetried(false);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setIsTyping(false);

      if (data.type === "error") {
        if (data.message.includes("message limit")) {
          toast(
            (t) => (
              <div className="flex flex-col gap-2">
                <span>
                  Monthly message limit reached. Please{" "}
                  <a
                    href="/pricing"
                    className="text-blue-400 hover:text-blue-300 underline transition-colors duration-200"
                    onClick={() => toast.dismiss(t.id)}
                  >
                    upgrade
                  </a>{" "}
                  your plan to continue chatting.
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
        } else {
          toast.error(data.message);
        }
      } else if (data.type === "reponse") {
        messagesQuery.refetch();
        setTimeout(scrollToBottom, 100); // Add scroll after message received
      }
    };

    ws.onerror = async (error) => {
      console.error("WebSocket error:", error);

      // Only attempt refresh once
      if (!hasRetried) {
        try {
          const refreshResponse = await refreshToken();
          setHasRetried(true);
          // Close existing connection if any
          if (websocketRef.current) {
            websocketRef.current.close();
          }
          // Retry connection with new token
          connectWebSocket(refreshResponse.access_token);
        } catch (refreshError) {
          console.error("Token refresh failed:", refreshError);
          toast.error("Failed to reconnect. Please try logging in again.");
        }
      } else {
        toast.error("Error connecting to chat server");
      }
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };
  };

  useEffect(() => {
    if (!accessToken || !selectedBotId) return;

    connectWebSocket(accessToken);

    return () => {
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        websocketRef.current.close();
      }
    };
  }, [accessToken, selectedBotId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !message.trim() ||
      !selectedBotId ||
      !websocketRef.current ||
      !currentConversation
    )
      return;

    try {
      const newMessage: Message = {
        id: Date.now().toString(),
        content: message.trim(),
        user_id: "user",
        conversation_id: currentConversation.id,
        created_at: new Date().toISOString(),
      };

      setLocalMessages((prev) => [...prev, newMessage]);
      setMessage("");
      setIsTyping(true);
      scrollToBottom();

      websocketRef.current.send(
        JSON.stringify({
          content: newMessage.content,
          bot_id: selectedBotId,
        })
      );
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message");
      setIsTyping(false);
    }
  };

  useEffect(() => {
    if (bots.data && bots.data.length > 0 && !selectedBotId) {
      setSelectedBotId(bots.data[0].bot_id);
    }
  }, [bots.data, selectedBotId]);

  useEffect(() => {
    scrollToBottom();
  }, [messagesQuery.data, localMessages]); // Update dependencies to include localMessages

  // Add useLayoutEffect for immediate scroll on local messages
  useLayoutEffect(() => {
    scrollToBottom();
  }, [localMessages]);

  useEffect(() => {
    if (currentConversation?.id) {
      messagesQuery.refetch();
    }
  }, [currentConversation?.id]);

  useEffect(() => {
    if (messagesQuery.data) {
      setLocalMessages([]);
      setIsTyping(false);
    }
  }, [messagesQuery.data]);

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
                    className={`h-8 w-8 rounded-full overflow-hidden border ${
                      selectedBot.gender === "Female"
                        ? "bg-pink-500/10 border-pink-500/20"
                        : "bg-blue-500/10 border-blue-500/20"
                    } flex items-center justify-center`}
                  >
                    {selectedBot.avatar_url ? (
                      <img
                        src={selectedBot.avatar_url}
                        alt={selectedBot.name}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <FontAwesomeIcon
                        icon={selectedBot.gender === "Female" ? faVenus : faMars}
                        className={
                          selectedBot.gender === "Female"
                            ? "text-pink-400"
                            : "text-blue-400"
                        }
                      />
                    )}
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
                        className={`h-8 w-8 rounded-full overflow-hidden border ${
                          bot.gender === "Female"
                            ? "bg-pink-500/10 border-pink-500/20"
                            : "bg-blue-500/10 border-blue-500/20"
                        } flex items-center justify-center`}
                      >
                        {bot.avatar_url ? (
                          <img
                            src={bot.avatar_url}
                            alt={bot.name}
                            className="h-full w-full object-cover"
                            loading="lazy"
                          />
                        ) : (
                          <FontAwesomeIcon
                            icon={bot.gender === "Female" ? faVenus : faMars}
                            size="xl"
                            className={
                              bot.gender === "Female"
                                ? "text-pink-400 filter-pink-400"
                                : "text-blue-400 filter-blue-400"
                            }
                          />
                        )}
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
          {[...(messagesQuery.data || []), ...localMessages].map((msg) => (
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

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="max-w-[70%] p-3 rounded-xl bg-white/5">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Message input */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-white/5">
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
