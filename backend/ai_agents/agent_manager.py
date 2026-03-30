from typing import Dict
from models.entities import Nation, GameState, AIType, AI_CONFIGS
from ai_agents.base_agent import BaseAIAgent
from ai_agents.deepseek.deepseek_agent import DeepSeekAgent
from ai_agents.aliyun.aliyun_agent import AliyunAgent
from ai_agents.kimi.kimi_agent import KimiAgent


class AIAgentManager:
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.agents: Dict[str, BaseAIAgent] = {}
    
    def initialize_agents(self, game_state: GameState):
        for nation_id, nation in game_state.nations.items():
            ai_type = nation.ai_type
            api_key = self.api_keys.get(ai_type.value)
            
            if ai_type == AIType.DEEPSEEK and api_key:
                self.agents[nation_id] = DeepSeekAgent(nation, api_key)
            elif ai_type == AIType.ALIYUN and api_key:
                self.agents[nation_id] = AliyunAgent(nation, api_key)
            elif ai_type == AIType.KIMI and api_key:
                self.agents[nation_id] = KimiAgent(nation, api_key)
    
    def get_agent(self, nation_id: str) -> BaseAIAgent:
        return self.agents.get(nation_id)
    
    def process_all_decisions(self, game_state: GameState) -> Dict:
        decisions = {}
        
        for nation_id, agent in self.agents.items():
            try:
                decision = agent.make_decision(game_state)
                decisions[nation_id] = decision
            except Exception as e:
                print(f"Error processing decision for {nation_id}: {e}")
                decisions[nation_id] = {
                    "action": "wait",
                    "target": None,
                    "reason": "决策处理失败"
                }
        
        return decisions
    
    def process_chat_message(self, nation_id: str, message: str, sender: str) -> str:
        agent = self.get_agent(nation_id)
        
        if agent:
            try:
                return agent.process_chat_message(message, sender)
            except Exception as e:
                print(f"Error processing chat for {nation_id}: {e}")
                return "我听到了你的声音，但现在无法回应。"
        
        return "未找到对应的AI。"
    
    def get_chat_history(self, nation_id: str):
        agent = self.get_agent(nation_id)
        
        if agent:
            return agent.get_chat_history()
        
        return []
