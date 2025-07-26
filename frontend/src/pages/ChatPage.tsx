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
import { useState, useEffect, useRef, useLayoutEffect, Suspense } from "react";
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

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useGLTF, Environment, PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";

interface AnimatedAvatarProps {
  url: string;
}

interface Message {
  id: string;
  content: string;
  user_id: string;
  conversation_id: string;
  created_at: string;
}

// Composant Avatar animé 3D
function AnimatedAvatar({ url }: AnimatedAvatarProps) {
  const group = useRef<any>(null);

  const { scene, nodes } = useGLTF(url);

  const head = nodes.Head;
  const leftArm = nodes.LeftArm;
  const rightArm = nodes.RightArm;

  const leftEyeLid = nodes.LeftEyeLid as THREE.Mesh | undefined;
  const rightEyeLid = nodes.RightEyeLid as THREE.Mesh | undefined;

  // --- Morph target sourire ---
  const faceMesh = nodes.FaceMesh as THREE.Mesh | undefined; // ADAPTE ICI le nom exact de ton mesh
  const smileIndex = faceMesh?.morphTargetDictionary?.Smile;
  const smileInfluences = faceMesh?.morphTargetInfluences;

  // Blink params
  const blinkDuration = 0.1;
  const blinkInterval = 4;
  const lastBlink = useRef(0);

  // Smile state
  const [isSmiling, setIsSmiling] = useState(false);
  const smileProgress = useRef(0); // entre 0 et 1

  useEffect(() => {
    // Toutes 8-15 secondes, déclenche un sourire de 2-4 secondes
    const interval = setInterval(() => {
      setIsSmiling(true);
      setTimeout(() => setIsSmiling(false), 2500 + Math.random() * 1500);
    }, 10000 + Math.random() * 5000);

    return () => clearInterval(interval);
  }, []);

  // Store previous time for delta calculation
  const prevTime = useRef<number>(0);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const delta = t - prevTime.current;
    prevTime.current = t;

    if (group.current) {
      // --- Mouvements tête ---
      if (head) {
        head.rotation.y = 0.1 * Math.sin(t * 0.7);
        head.rotation.x = 0.07 * Math.sin(t * 0.5);
        head.rotation.z = 0.03 * Math.sin(t * 0.3);
      }

      // --- Balancement bras ---
      if (leftArm) {
        const baseRotationX = 1;
        const amplitude = 0.04;
        const frequency = 1;
        const phaseLeft = 0; // phase du bras gauche

        leftArm.rotation.y = THREE.MathUtils.lerp(leftArm.rotation.y, 0, 0.02);
        leftArm.rotation.z = THREE.MathUtils.lerp(leftArm.rotation.z, 0, 0.02);
        leftArm.rotation.x = baseRotationX + amplitude * Math.sin(t * frequency + phaseLeft);
      }
      if (rightArm) {
        const baseRotationX = 1;
        const amplitude = 0.04;
        const frequency = 1;
        const phaseRight = 0.9; // phase du bras droit (ex: 1.2 radian, différent de Math.PI)

        rightArm.rotation.y = THREE.MathUtils.lerp(rightArm.rotation.y, 0, 0.02);
        rightArm.rotation.z = THREE.MathUtils.lerp(rightArm.rotation.z, 0, 0.02);
        rightArm.rotation.x = baseRotationX + amplitude * Math.sin(t * frequency + phaseRight);
      }

      // --- Clignement yeux ---
      if (leftEyeLid && rightEyeLid) {
        const timeSinceLastBlink = t - lastBlink.current;

        if (timeSinceLastBlink > blinkInterval + Math.random() * 2) {
          lastBlink.current = t;
        }

        const blinkProgress = (t - lastBlink.current) / blinkDuration;

        if (blinkProgress >= 0 && blinkProgress <= 1) {
          const opacity = blinkProgress <= 0.5
            ? THREE.MathUtils.lerp(1, 0, blinkProgress * 2)
            : THREE.MathUtils.lerp(0, 1, (blinkProgress - 0.5) * 2);

          if (!Array.isArray(leftEyeLid.material) && "opacity" in leftEyeLid.material) {
            (leftEyeLid.material as any).opacity = opacity;
            (leftEyeLid.material as any).transparent = true;
          }
          if (!Array.isArray(rightEyeLid.material) && "opacity" in rightEyeLid.material) {
            (rightEyeLid.material as any).opacity = opacity;
            (rightEyeLid.material as any).transparent = true;
          }
        } else {
          if (!Array.isArray(leftEyeLid.material) && "opacity" in leftEyeLid.material) {
            (leftEyeLid.material as any).opacity = 1;
          }
          if (!Array.isArray(rightEyeLid.material) && "opacity" in rightEyeLid.material) {
            (rightEyeLid.material as any).opacity = 1;
          }
        }
      }

      // --- Animation sourire ---
      if (smileInfluences && typeof smileIndex === "number") {
        if (isSmiling) {
          smileProgress.current = Math.min(smileProgress.current + delta, 1);
        } else {
          smileProgress.current = Math.max(smileProgress.current - delta, 0);
        }
        smileInfluences[smileIndex] = smileProgress.current;
      }
    }
  });

  return (
    <group ref={group} position={[0, 0, 0]}>
      <primitive object={scene} dispose={null} />
    </group>
  );
}

function FixedCamera({ position }: { position: [number, number, number] }) {
  const ref = useRef<any>(null);
  const { camera } = useThree();

  useEffect(() => {
    if (ref.current) {
      ref.current.position.set(...position);
      ref.current.lookAt(0, 0, 0);
      camera.position.copy(ref.current.position);
      camera.lookAt(0, 0.9, 0.1);
    }
  }, [position, camera]);

  return <PerspectiveCamera ref={ref} fov={65} makeDefault />;
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
  const [hasAccess, setHasAccess] = useState(true);

  const step = 2;
  const gridX = 0; 
  const gridY = 0.5;
  const cameraPosition: [number, number, number] = [gridX * step, gridY * step, 2];


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
        setTimeout(scrollToBottom, 100);
      }
    };

    ws.onerror = async (error) => {
      console.error("WebSocket error:", error);

      if (!hasRetried) {
        try {
          const refreshResponse = await refreshToken();
          setHasRetried(true);
          if (websocketRef.current) {
            websocketRef.current.close();
          }
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

    if (!hasAccess) {
      toast.error("Vous n'avez plus accès à cette conversation.");
      return;
    }
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
  }, [messagesQuery.data, localMessages]);

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
      setLocalMessages(messagesQuery.data.messages); // Le tableau messages
      setIsTyping(false);
      setHasAccess(messagesQuery.data.has_access); // L'accès
    }
  }, [messagesQuery.data]);
  return (
  <div className="h-full w-full flex bg-gradient-to-b to-[#050505] from-[#050505] rounded-3xl overflow-hidden border border-white/5">
    {/* Chat zone 70% */}
    <div className="flex flex-col w-[70%] h-full overflow-hidden">
      <div className="flex flex-col h-full overflow-y-auto no-scrollbar">
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
                  <span className="text-white font-medium">{selectedBot.name}</span>
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
                        selectedBotId === bot.bot_id ? "bg-violet-500/20" : "hover:bg-white/5"
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

                  <button
                    onClick={() => {
                      navigate("/dashboard/partners");
                      setIsDropDownOpen(false);
                    }}
                    className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors border-t border-white/5"
                  >
                    <div className="h-8 w-8 rounded-full bg-emerald-500/10 border-emerald-500/20 flex items-center justify-center border">
                      <FontAwesomeIcon icon={faPlus} className="text-emerald-400" />
                    </div>
                    <span className="text-white font-medium">Create New Companion</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Chat content area */}
        <div className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-4">
          {localMessages.map((msg) => (
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
          {!hasAccess && (
            <div className="flex justify-center my-4">
              <div className="max-w-[70%] p-3 rounded-xl bg-red-500/10 text-red-400 text-sm text-center">
                You no longer have access to this conversation. Please upgrade to a higher plan to continue chatting.
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
              disabled={!message.trim() || !currentConversation?.id || !hasAccess}
              className="p-3 rounded-xl bg-violet-500 hover:bg-violet-600 disabled:opacity-50 disabled:hover:bg-violet-500 transition-colors"
            >
              <FontAwesomeIcon icon={faPaperPlane} className="text-white" />
            </button>
          </div>
        </form>
      </div>
    </div>

    {/* Avatar 3D à droite 30% */}
    <div className="hidden md:flex w-[30%] h-full border-l border-white/5 relative items-center justify-center">
      <Canvas>
        <ambientLight intensity={0.6} />
        <directionalLight position={[0, 5, 5]} intensity={3} />
        <Suspense fallback={null}>
          {selectedBot?.url ? (
            <AnimatedAvatar url={selectedBot.url} />
          ) : (
            // Optionnel : un avatar par défaut ou rien
            <></>
          )}
        </Suspense>
        <FixedCamera position={cameraPosition} />
        <Environment preset="city" />
      </Canvas>
    </div>
  </div>
);


}
