from typing import Dict, List, Tuple
import random
from models.entities import Nation, GameState


class EventManager:
    def __init__(self):
        self.event_pool = self._initialize_event_pool()
    
    def _initialize_event_pool(self) -> List[Dict]:
        return [
            {
                "type": "natural_disaster",
                "name": "辐射尘暴",
                "description": "一场强烈的辐射尘暴袭击了你的领地",
                "effect": "resource_gain_rate -30%",
                "duration": 2,
                "options": [
                    {"text": "修建防护罩", "cost": {"food": 0, "energy": 0, "economy": 0}, "effect": "halve_impact"},
                    {"text": "强行硬抗", "cost": {}, "effect": "happiness -3"}
                ]
            },
            {
                "type": "natural_disaster",
                "name": "粮食歉收",
                "description": "由于气候异常，本季粮食产量大幅下降",
                "effect": "food_production -40%",
                "duration": 1,
                "options": [
                    {"text": "开放紧急储备", "cost": {"food": 50}, "effect": "no_loss"},
                    {"text": "实行配给制", "cost": {}, "effect": "happiness -5, cohesion +2"}
                ]
            },
            {
                "type": "natural_disaster",
                "name": "能源网络故障",
                "description": "主要能源网络出现故障",
                "effect": "energy -50, development_speed -50%",
                "duration": 1,
                "options": [
                    {"text": "派遣工程师抢修", "cost": {}, "risk": "population -10", "effect": "quick_repair"},
                    {"text": "等待自动恢复", "cost": {}, "effect": "double_loss"}
                ]
            },
            {
                "type": "social",
                "name": "科学家发现古代文献",
                "description": "你的科学家在废墟中发现了一批珍贵的古代文献",
                "effect": "potential_tech_unlock",
                "duration": 0,
                "options": [
                    {"text": "公之于众", "cost": {}, "effect": "prestige +10"},
                    {"text": "秘密研究", "cost": {}, "effect": "get_tech_no_diplomacy"}
                ]
            },
            {
                "type": "social",
                "name": "难民潮",
                "description": "一群难民来到了你的边境",
                "effect": "population +20-50",
                "duration": 0,
                "options": [
                    {"text": "全部接纳", "cost": {}, "effect": "happiness +3, resource_pressure"},
                    {"text": "选择性接收", "cost": {}, "effect": "population +10, prestige +5"},
                    {"text": "关闭边境", "cost": {}, "effect": "prestige -15"}
                ]
            },
            {
                "type": "social",
                "name": "艺术家运动",
                "description": "人民开始渴望精神文化生活",
                "effect": "cultural_demand",
                "duration": 0,
                "options": [
                    {"text": "支持艺术", "cost": {"food": 10, "energy": 10}, "effect": "happiness +5"},
                    {"text": "镇压", "cost": {}, "effect": "cohesion +3, happiness -8"}
                ]
            }
        ]
    
    def check_event_trigger(self) -> bool:
        return random.random() < 0.1
    
    def trigger_random_event(self, nation: Nation) -> Dict:
        event = random.choice(self.event_pool)
        return event
    
    def apply_event_effect(self, nation: Nation, event: Dict, choice: int):
        if choice < len(event["options"]):
            option = event["options"][choice]
            cost = option.get("cost", {})
            
            if cost:
                nation.resources.food -= cost.get("food", 0)
                nation.resources.energy -= cost.get("energy", 0)
                nation.resources.economy -= cost.get("economy", 0)
            
            effect = option.get("effect", "")
            
            if "happiness" in effect:
                change = self._parse_attribute_change(effect, "happiness")
                nation.attributes.happiness += change
            
            if "cohesion" in effect:
                change = self._parse_attribute_change(effect, "cohesion")
                nation.attributes.cohesion += change
            
            if "prestige" in effect:
                change = self._parse_attribute_change(effect, "prestige")
                nation.attributes.prestige += change
            
            if "population" in effect:
                change = self._parse_attribute_change(effect, "population")
                nation.population = max(1, nation.population + change)
    
    def _parse_attribute_change(self, effect: str, attribute: str) -> int:
        parts = effect.split(", ")
        for part in parts:
            if attribute in part:
                sign = 1 if "+" in part else -1
                value = int(part.split()[-1])
                return sign * value
        return 0
