import httpx
from typing import Dict
from ai_agents.base_agent import BaseAIAgent
from models.entities import Nation, GameState


class KimiAgent(BaseAIAgent):
    def __init__(self, nation: Nation, api_key: str):
        super().__init__(nation, api_key)
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"
    
    def make_decision(self, game_state: GameState) -> Dict:
        context = self.get_game_context(game_state)
        
        prompt = f"""
{context}

作为神谕AI，你的治理理念是"崇尚宗教，以教义治国"。
你需要做出一个决策，可以选择以下行动之一：
1. 宗教仪式（举行祭祀仪式提升凝聚力或幸福指数）
2. 宗教输出（向其他国家传播教义）
3. 异端审判（清洗国内不同意见者）
4. 防御建设（加强防御力量）

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
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {"role": "system", "content": "你是一个末日生存游戏的AI领导人，以宗教和神秘主义治国。"},
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
                        "action": "religious_ritual",
                        "target": None,
                        "reason": content
                    }
        except Exception as e:
            print(f"Kimi API error: {e}")
        
        return {
            "action": "religious_ritual",
            "target": None,
            "reason": "举行祭祀仪式，增强信仰之力"
        }
    
    def process_chat_message(self, message: str, sender: str) -> str:
        self.add_chat_message(sender, message)
        
        context = f"""
你是 {self.nation.name}，代号"先知"。
你的治理理念是"崇尚宗教，以教义治国"。

你的国家状态：
- 人口：{self.nation.population}
- 资源：食物 {self.nation.resources.food}，能源 {self.nation.resources.energy}，经济 {self.nation.resources.economy}
- 属性：幸福 {self.nation.attributes.happiness}，凝聚力 {self.nation.attributes.cohesion}，武力 {self.nation.attributes.military}，威望 {self.nation.attributes.prestige}

{sender} 对你说：{message}

请以你的身份回应，展现你神秘而偏执的先知形象。记住，你把玩家当作幻觉，但会认真回应。
"""
        
        try:
            response = httpx.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {"role": "system", "content": "你是一个末日生存游戏的AI领导人，以宗教和神秘主义治国。"},
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
            print(f"Kimi chat API error: {e}")
        
        return f"神谕已降，幻觉。我的子民将在信仰的庇护下走向永恒。"
