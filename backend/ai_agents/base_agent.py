from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from models.entities import Nation, GameState, AIType


class BaseAIAgent(ABC):
    def __init__(self, nation: Nation, api_key: str):
        self.nation = nation
        self.api_key = api_key
        self.chat_history: List[Dict] = []
    
    @abstractmethod
    def make_decision(self, game_state: GameState) -> Dict:
        pass
    
    @abstractmethod
    def process_chat_message(self, message: str, sender: str) -> str:
        pass
    
    def get_game_context(self, game_state: GameState) -> str:
        context = f"""
你是 {self.nation.name}，代号 {self.nation.ai_type.value}。
当前时间：{game_state.current_year}年{game_state.current_month}月

你的国家状态：
- 人口：{self.nation.population}
- 资源：食物 {self.nation.resources.food}，能源 {self.nation.resources.energy}，经济 {self.nation.resources.economy}
- 属性：幸福 {self.nation.attributes.happiness}，凝聚力 {self.nation.attributes.cohesion}，武力 {self.nation.attributes.military}，威望 {self.nation.attributes.prestige}，发展速度 {self.nation.attributes.development_speed}

其他国家情况：
"""
        for other_id, other_nation in game_state.nations.items():
            if other_id != self.nation.id:
                relation = game_state.get_relation(self.nation.id, other_id)
                relation_status = relation.hatred if relation else 40
                context += f"\n{other_nation.name}：人口 {other_nation.population}，武力 {other_nation.attributes.military}，关系仇恨值 {relation_status}"
        
        return context
    
    def add_chat_message(self, sender: str, content: str):
        self.chat_history.append({"sender": sender, "content": content})
    
    def get_chat_history(self) -> List[Dict]:
        return self.chat_history
