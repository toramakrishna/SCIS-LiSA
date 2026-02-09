import { create } from 'zustand';
import type { QueryResponse } from '@/types';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  queryResponse?: QueryResponse;
}

interface QueryStore {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  addUserMessage: (content: string) => void;
  addAssistantMessage: (data: { content: string; queryResponse?: QueryResponse }) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
}

export const useQueryStore = create<QueryStore>((set) => ({
  messages: [],
  isLoading: false,
  error: null,

  addUserMessage: (content: string) => {
    const message: Message = {
      id: `user-${Date.now()}-${Math.random()}`,
      type: 'user',
      content,
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  addAssistantMessage: (data: { content: string; queryResponse?: QueryResponse }) => {
    const message: Message = {
      id: `assistant-${Date.now()}-${Math.random()}`,
      type: 'assistant',
      content: data.content,
      timestamp: new Date(),
      queryResponse: data.queryResponse,
    };
    set((state) => ({
      messages: [...state.messages, message],
      isLoading: false,
    }));
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setError: (error: string | null) => {
    set({ error, isLoading: false });
  },

  clearMessages: () => {
    set({ messages: [], error: null });
  },
}));
