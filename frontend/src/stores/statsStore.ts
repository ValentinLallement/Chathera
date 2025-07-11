import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Conversation {
  id: string;
  botName: string;
  lastMessage: string;
  timestamp: string;
  unread: boolean;
  affection: number;
  personality: string;
  messageCount: number;
}

interface StatsState {
  conversations: Conversation[];
  remainingMessages: number;
  hotPicsLeft: number;
  longestStreak: number;
  addConversation: (conversation: Conversation) => void;
  updateAffection: (botId: string, messageCount: number) => void;
  setRemainingMessages: (count: number) => void;
  setHotPicsLeft: (count: number) => void;
  setLongestStreak: (days: number) => void;
}

export const useStatsStore = create<StatsState>()(
  persist(
    (set) => ({
      conversations: [],
      remainingMessages: 242,
      hotPicsLeft: 7,
      longestStreak: 15,

      addConversation: (conversation) =>
        set((state) => ({
          conversations: [...state.conversations, conversation],
        })),

      updateAffection: (botId, messageCount) =>
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === botId
              ? {
                  ...conv,
                  messageCount,
                  // Calculate affection based on message count - more messages = higher affection
                  affection: Math.min(Math.floor((messageCount / 100) * 100), 100),
                }
              : conv
          ),
        })),

      setRemainingMessages: (count) => set({ remainingMessages: count }),
      setHotPicsLeft: (count) => set({ hotPicsLeft: count }),
      setLongestStreak: (days) => set({ longestStreak: days }),
    }),
    {
      name: 'stats-storage',
      partialize: (state) => ({
        conversations: state.conversations,
        remainingMessages: state.remainingMessages,
        hotPicsLeft: state.hotPicsLeft,
        longestStreak: state.longestStreak,
      }),
    }
  )
);