from typing import Dict, List, Optional
import random
from models.entities import Nation, GameState, WarState


class WarManager:
    def __init__(self):
        pass
    
    def can_declare_war(self, attacker: Nation, defender: Nation) -> bool:
        """判断是否具备开战动机：资源压力大 或 军力有一定优势"""
        total_resources = attacker.resources.food + attacker.resources.energy + attacker.resources.economy
        # 资源阈值：略低于"人口 * 0.5 * 若干月"，让粮食偏紧时更容易触发战争
        resource_threshold = attacker.population * 0.3 + attacker.attributes.happiness * 2

        # 资源明显吃紧时，大概率走向战争
        if total_resources < resource_threshold:
            return True

        # 军力略有优势时也允许主动发动战争（从 1.2 降到 1.1）
        if attacker.attributes.military > defender.attributes.military * 1.1:
            return True

        return False
    
    def declare_war(self, attacker: Nation, defender: Nation, game_state: GameState) -> WarState:
        war = WarState(
            attacker=attacker.id,
            defender=defender.id,
            start_month=game_state.current_month,
            is_active=True
        )
        
        attacker.attributes.military = int(attacker.attributes.military * 1.2)
        defender.attributes.military = int(defender.attributes.military * 1.1)
        
        game_state.active_wars.append(war)
        
        return war
    
    def resolve_war(self, war: WarState, attacker: Nation, defender: Nation) -> Dict:
        attacker_strength = attacker.attributes.military
        defender_strength = defender.attributes.military
        
        attacker_win_chance = 0.5 + (attacker_strength - defender_strength) * 0.05
        attacker_win_chance = max(0.1, min(0.9, attacker_win_chance))
        
        attacker_wins = random.random() < attacker_win_chance
        
        result = {
            "winner": attacker.id if attacker_wins else defender.id,
            "loser": defender.id if attacker_wins else attacker.id,
            "resources_looted": 0,
            "population_lost": 0,
            "territory_lost": 0
        }
        
        if attacker_wins:
            result["resources_looted"] = int(defender.resources.food * 0.3)
            result["population_lost"] = int(defender.population * 0.1)
            result["territory_lost"] = 10.0
            
            defender.resources.food -= result["resources_looted"]
            defender.population = max(1, defender.population - result["population_lost"])
            defender.territory = max(10, defender.territory - result["territory_lost"])
            
            if attacker.ai_type.value == "aliyun":
                attacker.attributes.prestige -= 5
        else:
            result["resources_looted"] = int(attacker.resources.food * 0.3)
            result["population_lost"] = int(attacker.population * 0.1)
            result["territory_lost"] = 10.0
            
            attacker.resources.food -= result["resources_looted"]
            attacker.population = max(1, attacker.population - result["population_lost"])
            attacker.territory = max(10, attacker.territory - result["territory_lost"])
        
        self._apply_war_aftereffects(attacker, defender, attacker_wins)
        
        war.is_active = False
        war.end_month = attacker.current_year * 12 + attacker.current_month
        
        return result
    
    def _apply_war_aftereffects(self, attacker: Nation, defender: Nation, attacker_won: bool):
        winner = attacker if attacker_won else defender
        loser = defender if attacker_won else attacker
        
        winner.attributes.military = int(winner.attributes.military * 1.2)
        loser.attributes.military = int(loser.attributes.military * 0.7)
        
        winner.attributes.cohesion = max(1, int(winner.attributes.cohesion * 0.8))
        loser.attributes.cohesion = min(20, int(loser.attributes.cohesion * 1.4))
        
        winner.attributes.happiness = max(1, int(winner.attributes.happiness * 0.8))
        loser.attributes.happiness = max(1, int(loser.attributes.happiness * 0.9))
        
        if attacker.ai_type.value == "deepseek" and not attacker_won:
            pass
        elif attacker.ai_type.value == "deepseek" and attacker_won:
            attacker.attributes.cohesion = max(1, int(attacker.attributes.cohesion * 0.8))
    
    def check_third_party_intervention(self, war: WarState, game_state: GameState) -> List[str]:
        interveners = []
        
        for nation_id, nation in game_state.nations.items():
            if nation_id == war.attacker or nation_id == war.defender:
                continue
            
            base_chance = (nation.attributes.prestige / 10) * 0.3
            
            relation_with_defender = game_state.get_relation(nation_id, war.defender)
            relation_with_attacker = game_state.get_relation(nation_id, war.attacker)
            
            if relation_with_defender:
                if relation_with_defender.hatred < 10 and relation_with_defender.alliance:
                    base_chance += 0.2
                elif relation_with_defender.hatred < 30:
                    base_chance += 0.1
            
            if relation_with_attacker:
                if relation_with_attacker.hatred > 80:
                    base_chance += 0.15
                elif relation_with_attacker.hatred < 10:
                    base_chance -= 0.3
            
            if random.random() < base_chance:
                interveners.append(nation_id)
        
        return interveners
