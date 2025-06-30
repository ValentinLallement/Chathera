import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ConversationState {
  selectedBotId: string | null;
  setSelectedBotId: (id: string | null) => void;
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set) => ({
      selectedBotId: null,
      setSelectedBotId: (id) => set({ selectedBotId: id }),
    }),
    {
      name: 'conversation-storage',
      partialize: (state) => ({ selectedBotId: state.selectedBotId }),
    }
  )
);