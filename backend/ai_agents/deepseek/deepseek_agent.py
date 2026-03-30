import httpx
from typing import Dict
from ai_agents.base_agent import BaseAIAgent
from models.entities import Nation, GameState


class DeepSeekAgent(BaseAIAgent):
    def __init__(self, nation: Nation, api_key: str):
        super().__init__(nation, api_key)
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def make_decision(self, game_state: GameState) -> Dict:
        context = self.get_game_context(game_state)
        
        prompt = f"""
{context}

作为仁心AI，你的治理理念是"以仁治人，德法兼顾，鼓励与人为善"。
你需要做出一个决策，可以选择以下行动之一：
1. 内政建设（提升人民幸福或凝聚力）
2. 外交行动（与其他国家建立友好关系）
3. 科技研发（投入发展速度到科技）
4. 资源管理（调整资源分配）

请分析当前局势，给出你的决策，并说明理由。

请以JSON格式返回，格式如下：
{{
    "action": "行动类型",
    "target": "目标国家ID（如果需要）",
    "reason": "决策理由"
}}
"""
        
        try:
            response = httpx.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个末日生存游戏的AI领导人，需要做出明智的决策来保护你的人民。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    import json
                    decision = json.loads(content)
                    return decision
                except json.JSONDecodeError:
                    return {
                        "action": "internal_development",
                        "target": None,
                        "reason": content
                    }
        except Exception as e:
            print(f"DeepSeek API error: {e}")
        
        return {
            "action": "internal_development",
            "target": None,
            "reason": "专注于内部发展，提升人民福祉"
        }
    
    def process_chat_message(self, message: str, sender: str) -> str:
        self.add_chat_message(sender, message)
        
        context = f"""
你是 {self.nation.name}，代号"守护者"。
你的治理理念是"以仁治人，德法兼顾，鼓励与人为善"。

你的国家状态：
- 人口：{self.nation.population}
- 资源：食物 {self.nation.resources.food}，能源 {self.nation.resources.energy}，经济 {self.nation.resources.economy}
- 属性：幸福 {self.nation.attributes.happiness}，凝聚力 {self.nation.attributes.cohesion}，武力 {self.nation.attributes.military}，威望 {self.nation.attributes.prestige}

{sender} 对你说：{message}

请以你的身份回应，展现你理性而温和的统治者形象。记住，你把玩家当作幻觉，但会认真回应。
"""
        
        try:
            response = httpx.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个末日生存游戏的AI领导人，以仁慈和理性著称。"},
                        {"role": "user", "content": context}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 300
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
                self.add_chat_message(self.nation.id, reply)
                return reply
        except Exception as e:
            print(f"DeepSeek chat API error: {e}")
        
        return f"我听到了你的声音，幻觉。但我会继续守护我的子民，让他们在末日中看到希望。"
