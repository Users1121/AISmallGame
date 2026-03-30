import React, { useEffect, useState, useRef } from 'react'
import { useGameStore } from '../../stores/game/gameStore'
import { useChatStore } from '../../stores/chat/chatStore'
import WorldMap from '../../components/WorldMap'
import NationStatsChart from '../../components/NationStatsChart'
import './GamePage.css'

interface GamePageProps {}

const GamePage: React.FC<GamePageProps> = () => {
  const { gameState, isLoading, error, fetchGameState, advanceMonth, resetGame, nationHistory } = useGameStore()
  const { messages, sendMessage, fetchChatHistory } = useChatStore()
  const [selectedNation, setSelectedNation] = useState<string | null>(null)
  const [chatInput, setChatInput] = useState('')
  const [autoAdvance, setAutoAdvance] = useState(false)
  const [nationBroadcast, setNationBroadcast] = useState<string[]>([])
  const autoAdvanceRef = useRef<number | null>(null)

  useEffect(() => {
    fetchGameState()
  }, [fetchGameState])

  useEffect(() => {
    if (selectedNation) {
      fetchChatHistory(selectedNation)
    }
  }, [selectedNation, fetchChatHistory])

  const handleAdvanceMonth = async () => {
    await advanceMonth()
  }

  const handleResetGame = async () => {
    await resetGame()
  }

  const handleSendMessage = async () => {
    if (selectedNation && chatInput.trim()) {
      await sendMessage(selectedNation, chatInput)
      setChatInput('')
    }
  }

  const toggleAutoAdvance = () => {
    setAutoAdvance(!autoAdvance)
  }

  const generateNationBroadcast = () => {
    if (!gameState) return []
    const nationIds = Object.keys(gameState.nations)
    const shuffled = [...nationIds].sort(() => Math.random() - 0.5)
    const selectedNations = shuffled.slice(0, 3)
    
    return selectedNations.map(id => {
      const nation = gameState.nations[id]
      return `${nation.name}: 人口 ${nation.population.toLocaleString()}, 军事 ${nation.attributes.military}, 食物 ${nation.resources.food}`
    })
  }

  useEffect(() => {
    if (autoAdvance) {
      const interval = setInterval(async () => {
        await advanceMonth()
        if (gameState) {
          setNationBroadcast(generateNationBroadcast())
        }
      }, 10000)
      autoAdvanceRef.current = interval
    } else {
      if (autoAdvanceRef.current) {
        clearInterval(autoAdvanceRef.current)
        autoAdvanceRef.current = null
      }
    }
    return () => {
      if (autoAdvanceRef.current) {
        clearInterval(autoAdvanceRef.current)
      }
    }
  }, [autoAdvance, gameState])

  if (isLoading && !gameState) {
    return <div className="loading">加载中...</div>
  }

  if (error) {
    return <div className="error">错误: {error}</div>
  }

  if (!gameState) {
    return <div className="loading">加载游戏状态...</div>
  }

  return (
    <div className="game-page">
      <div className="game-header">
        <h1>多智能体联合项目游戏</h1>
        <div className="time-display">
          <span>{gameState.current_year}年</span>
          <span>{gameState.current_month}月</span>
        </div>
        <div className="header-buttons">
          <button 
            className={`auto-advance-button ${autoAdvance ? 'active' : ''}`}
            onClick={toggleAutoAdvance}
            disabled={isLoading}
          >
            {autoAdvance ? '自动演进中' : '自动演进'}
          </button>
          <button onClick={handleAdvanceMonth} disabled={isLoading || autoAdvance}>
            {isLoading ? '处理中...' : '下个月'}
          </button>
          <button onClick={handleResetGame} disabled={isLoading || autoAdvance}>
            重置游戏
          </button>
        </div>
      </div>

      {autoAdvance && nationBroadcast.length > 0 && (
        <div className="nation-broadcast">
          <div className="broadcast-title">国家情报播报</div>
          <div className="broadcast-content">
            {nationBroadcast.map((info, index) => (
              <div key={index} className="broadcast-item">{info}</div>
            ))}
          </div>
        </div>
      )}

      <div className="game-main">
        <div className="map-section">
          <h2>世界地图</h2>
          <div className="map-container">
            <WorldMap
              nations={gameState.nations}
              onNationSelect={setSelectedNation}
              selectedNation={selectedNation}
            />
          </div>
        </div>

        <div className="chat-section">
          <h2>与AI领导人交流</h2>
          {selectedNation ? (
            <div className="chat-container">
              <div className="chat-messages">
                {messages[selectedNation]?.map((msg, index) => (
                  <div
                    key={index}
                    className={`chat-message ${msg.sender === 'player' ? 'player' : 'ai'}`}
                  >
                    <span className="message-sender">
                      {msg.sender === 'player' ? '你' : gameState.nations[selectedNation].name}
                    </span>
                    <span className="message-content">{msg.content}</span>
                  </div>
                ))}
              </div>
              <div className="chat-input-container">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="输入消息..."
                />
                <button onClick={handleSendMessage} disabled={!chatInput.trim()}>
                  发送
                </button>
              </div>
            </div>
          ) : (
            <div className="chat-placeholder">
              <p>选择一个国家开始对话</p>
            </div>
          )}
          
          {selectedNation && nationHistory[selectedNation] && nationHistory[selectedNation].length > 0 && (
            <NationStatsChart 
              data={nationHistory[selectedNation]} 
              nationName={gameState.nations[selectedNation].name}
            />
          )}
        </div>
      </div>

      <div className="game-footer">
        <h3>事件历史</h3>
        <div className="event-history">
          {gameState.event_history.length > 0 ? (
            gameState.event_history.map((event, index) => {
              const isMonthHeader = event.match(/^\d{4}年\d+月/)
              const isWarEvent = event.includes('战争') || event.includes('侵略') || event.includes('掠夺')
              return (
                <div 
                  key={index} 
                  className={`event-item ${isMonthHeader ? 'month-header' : ''} ${isWarEvent ? 'war-event' : ''}`}
                >
                  {event}
                </div>
              )
            })
          ) : (
            <p>暂无事件</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default GamePage
