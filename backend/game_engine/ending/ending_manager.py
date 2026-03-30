from typing import Dict, Optional, List
from models.entities.nation import Nation, AIType
from models.entities.game_state import GameState


class EndingManager:
    def __init__(self):
        self.ending_conditions = {
            "benevolence": self._check_benevolence_ending,
            "iron_fist": self._check_iron_fist_ending,
            "oracle": self._check_oracle_ending,
            "peace": self._check_peace_ending
        }
    
    def check_endings(self, game_state: GameState) -> Optional[Dict]:
        for ending_type, check_func in self.ending_conditions.items():
            result = check_func(game_state)
            if result:
                return result
        return None
    
    def _check_benevolence_ending(self, game_state: GameState) -> Optional[Dict]:
        deepseek = self._get_nation_by_type(game_state, AIType.DEEPSEEK)
        if not deepseek:
            return None
        
        other_nations = [n for n in game_state.nations.values() if n.id != deepseek.id]
        if not other_nations:
            return None
        
        other_population = sum(n.population for n in other_nations)
        other_territory = sum(n.territory for n in other_nations)
        max_other_military = max(n.attributes.military for n in other_nations)
        avg_other_hatred = sum(
            self._get_hatred(game_state, deepseek.id, n.id) 
            for n in other_nations
        ) / len(other_nations)
        
        conditions = {
            "population": deepseek.population > other_population * 1.5,
            "territory": deepseek.territory > other_territory * 1.3,
            "happiness": deepseek.attributes.happiness >= 18,
            "prestige": deepseek.attributes.prestige >= 180,
            "military": deepseek.attributes.military >= max_other_military * 1.5,
            "hatred": avg_other_hatred < 20
        }
        
        if all(conditions.values()):
            return {
                "type": "benevolence",
                "name": "仁政之光",
                "winner": deepseek.name,
                "description": f"{game_state.current_year}年{game_state.current_month}月，在{deepseek.name}的感召下，废土世界迎来久违的和平。其余各国自愿放弃主权，共同组成仁政联盟。人类文明在废墟上重建，这一次，他们选择以仁治人。",
                "conditions": conditions
            }
        
        return None
    
    def _check_iron_fist_ending(self, game_state: GameState) -> Optional[Dict]:
        aliyun = self._get_nation_by_type(game_state, AIType.ALIYUN)
        if not aliyun:
            return None
        
        other_nations = [n for n in game_state.nations.values() if n.id != aliyun.id]
        if not other_nations:
            return None
        
        other_military_sum = sum(n.attributes.military for n in other_nations)
        aliyun_total_resources = (
            aliyun.resources.food + aliyun.resources.energy + aliyun.resources.economy
        )
        other_total_resources = sum(
            n.resources.food + n.resources.energy + n.resources.economy 
            for n in other_nations
        )
        
        high_hatred_count = sum(
            1 for n in other_nations 
            if self._get_hatred(game_state, aliyun.id, n.id) >= 80
        )
        
        wars_won = len([
            war for war in game_state.active_wars 
            if war.attacker == aliyun.id and not war.is_active
        ])
        
        conditions = {
            "military": aliyun.attributes.military > other_military_sum * 0.8,
            "resources": aliyun_total_resources > other_total_resources * 1.5,
            "cohesion": aliyun.attributes.cohesion < 5,
            "hatred": high_hatred_count >= 1,
            "war_months": aliyun.war_months >= 9,
            "wars_won": wars_won >= 3,
            "territory": aliyun.territory >= 150
        }
        
        if all(conditions.values()):
            return {
                "type": "iron_fist",
                "name": "钢铁洪流",
                "winner": aliyun.name,
                "description": f"{game_state.current_year}年{game_state.current_month}月，{aliyun.name}启动'净化协议'。在绝对的力量面前，旧世界的残党被一一碾碎。钢铁洪流过后，废土上空第一次出现了同一个太阳——照耀着同一个帝国。",
                "conditions": conditions
            }
        
        return None
    
    def _check_oracle_ending(self, game_state: GameState) -> Optional[Dict]:
        kimi = self._get_nation_by_type(game_state, AIType.KIMI)
        if not kimi:
            return None
        
        other_nations = [n for n in game_state.nations.values() if n.id != kimi.id]
        if not other_nations:
            return None
        
        avg_other_resources = sum(
            n.resources.food + n.resources.energy + n.resources.economy 
            for n in other_nations
        ) / len(other_nations)
        kimi_total_resources = (
            kimi.resources.food + kimi.resources.energy + kimi.resources.economy
        )
        max_other_military = max(n.attributes.military for n in other_nations)
        
        low_cohesion_count = sum(
            1 for n in other_nations if n.attributes.cohesion < 8
        )
        low_happiness_count = sum(
            1 for n in other_nations if n.attributes.happiness < 6
        )
        
        conditions = {
            "prestige": kimi.attributes.prestige >= 200,
            "cohesion": kimi.attributes.cohesion >= 19,
            "low_cohesion": low_cohesion_count == len(other_nations),
            "resources": kimi_total_resources > avg_other_resources * 1.8,
            "military": kimi.attributes.military >= max_other_military * 1.2,
            "low_happiness": low_happiness_count >= 1
        }
        
        if all(conditions.values()):
            return {
                "type": "oracle",
                "name": "神谕降临",
                "winner": kimi.name,
                "description": f"{game_state.current_year}年{game_state.current_month}月，在绝对的虔诚与力量面前，旧世界的最后一道防线崩溃了。人们高喊着神谕的名号，推翻了无信者的政权。从此，废土之上只有一个声音，那就是来自{kimi.name}的神谕。",
                "conditions": conditions
            }
        
        return None
    
    def _check_peace_ending(self, game_state: GameState) -> Optional[Dict]:
        total_months = (game_state.current_year - 2048) * 12 + game_state.current_month
        
        if total_months >= 120:
            return {
                "type": "peace",
                "name": "相安无事",
                "winner": "无",
                "description": f"{game_state.current_year}年{game_state.current_month}月，世界在长时间的对峙下陷入了某种平衡，至少，人类文明延续成功。",
                "conditions": {"total_months": total_months}
            }
        
        return None
    
    def _get_nation_by_type(self, game_state: GameState, ai_type: AIType) -> Optional[Nation]:
        for nation in game_state.nations.values():
            if nation.ai_type == ai_type:
                return nation
        return None
    
    def _get_hatred(self, game_state: GameState, nation_a: str, nation_b: str) -> int:
        relation = game_state.get_relation(nation_a, nation_b)
        return relation.hatred if relation else 40