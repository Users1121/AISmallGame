import { create } from 'zustand'

interface ChatMessage {
  sender: string
  content: string
  timestamp: string
}

interface ChatStore {
  messages: Record<string, ChatMessage[]>
  isLoading: boolean
  sendMessage: (nationId: string, content: string) => Promise<void>
  fetchChatHistory: (nationId: string) => Promise<void>
  addMessage: (nationId: string, message: ChatMessage) => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: {},
  isLoading: false,

  sendMessage: async (nationId: string, content: string) => {
    set({ isLoading: true })
    try {
      const response = await fetch(`http://localhost:8000/game/chat/${nationId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, sender: 'player' }),
      })
      if (!response.ok) throw new Error('Failed to send message')
      const data = await response.json()
      
      set((state) => ({
        messages: {
          ...state.messages,
          [nationId]: [
            ...(state.messages[nationId] || []),
            { sender: 'player', content, timestamp: new Date().toISOString() },
            { sender: nationId, content: data.response, timestamp: new Date().toISOString() },
          ],
        },
        isLoading: false,
      }))
    } catch (error) {
      console.error('Failed to send message:', error)
      set({ isLoading: false })
    }
  },

  fetchChatHistory: async (nationId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/game/chat/${nationId}`)
      if (!response.ok) throw new Error('Failed to fetch chat history')
      const data = await response.json()
      set((state) => ({
        messages: {
          ...state.messages,
          [nationId]: data.history || [],
        },
      }))
    } catch (error) {
      console.error('Failed to fetch chat history:', error)
    }
  },

  addMessage: (nationId: string, message: ChatMessage) => {
    set((state) => ({
      messages: {
        ...state.messages,
        [nationId]: [...(state.messages[nationId] || []), message],
      },
    }))
  },
}))
