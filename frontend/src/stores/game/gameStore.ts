import { create } from 'zustand'

export interface Nation {
  id: string
  name: string
  ai_type: string
  resources: {
    food: number
    energy: number
    economy: number
  }
  attributes: {
    happiness: number
    cohesion: number
    military: number
    prestige: number
    development_speed: number
  }
  tech_tree: {
    military_level: number
    social_level: number
    exploration_level: number
  }
  population: number
  territory: number
  color: string
}

export interface NationHistoryData {
  month: string
  food: number
  population: number
  economy: number
  energy: number
}

export interface GameState {
  current_month: number
  current_year: number
  nations: Record<string, Nation>
  diplomatic_relations: Array<{
    nation_a: string
    nation_b: string
    hatred: number
    alliance: boolean
    trade_agreement: boolean
  }>
  active_wars: Array<{
    attacker: string
    defender: string
    start_month: number
    is_active: boolean
  }>
  event_history: string[]
}

interface GameStore {
  gameState: GameState | null
  isLoading: boolean
  error: string | null
  nationHistory: Record<string, NationHistoryData[]>
  fetchGameState: () => Promise<void>
  advanceMonth: () => Promise<void>
  handlePlayerAction: (action: any) => Promise<void>
  resetGame: () => Promise<void>
}

export const useGameStore = create<GameStore>((set, get) => ({
  gameState: null,
  isLoading: false,
  error: null,
  nationHistory: {},

  fetchGameState: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch('http://localhost:8000/game/state')
      if (!response.ok) throw new Error('Failed to fetch game state')
      const data = await response.json()
      
      if (data && data.nations) {
        const currentHistory = get().nationHistory
        const monthLabel = `${data.current_year}年${data.current_month}月`
        
        if (Object.keys(currentHistory).length === 0) {
          const newHistory: Record<string, NationHistoryData[]> = {}
          Object.entries(data.nations).forEach(([nationId, nation]: [string, any]) => {
            newHistory[nationId] = [{
              month: monthLabel,
              food: nation.resources.food,
              population: nation.population,
              economy: nation.resources.economy,
              energy: nation.resources.energy
            }]
          })
          set({ gameState: data, isLoading: false, nationHistory: newHistory })
        } else {
          set({ gameState: data, isLoading: false })
        }
      } else {
        set({ gameState: data, isLoading: false })
      }
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
    }
  },

  advanceMonth: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch('http://localhost:8000/game/advance', {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to advance month')
      const result = await response.json()
      
      await get().fetchGameState()
      
      const currentState = get().gameState
      if (currentState) {
        const monthLabel = `${currentState.current_year}年${currentState.current_month}月`
        
        const currentHistory = get().nationHistory
        const newHistory: Record<string, NationHistoryData[]> = {}
        
        Object.entries(currentState.nations).forEach(([nationId, nation]) => {
          const nationHistoryData = currentHistory[nationId] || []
          
          const newData = {
            month: monthLabel,
            food: nation.resources.food,
            population: nation.population,
            economy: nation.resources.economy,
            energy: nation.resources.energy
          }
          
          if (nationHistoryData.length === 0) {
            newHistory[nationId] = [newData]
          } else {
            const lastData = nationHistoryData[nationHistoryData.length - 1]
            if (lastData.month === monthLabel) {
              newHistory[nationId] = nationHistoryData
            } else {
              newHistory[nationId] = [...nationHistoryData, newData]
              if (newHistory[nationId].length > 24) {
                newHistory[nationId] = newHistory[nationId].slice(-24)
              }
            }
          }
        })
        
        set({ nationHistory: newHistory })
      }
      
      set({ isLoading: false })
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
    }
  },

  handlePlayerAction: async (action) => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch('http://localhost:8000/game/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      })
      if (!response.ok) throw new Error('Failed to handle action')
      const data = await response.json()
      await get().fetchGameState()
      set({ isLoading: false })
      return data
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
      throw error
    }
  },

  resetGame: async () => {
    set({ isLoading: true, error: null, nationHistory: {} })
    try {
      const response = await fetch('http://localhost:8000/game/reset', {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to reset game')
      await get().fetchGameState()
      set({ isLoading: false })
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
    }
  },
}))
