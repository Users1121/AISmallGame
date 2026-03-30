from typing import Dict, List, Optional
import random
from models.entities import Nation, GameState, DiplomaticRelation


class DiplomacyManager:
    def __init__(self):
        pass
    
    def initialize_relations(self, game_state: GameState):
        nation_ids = list(game_state.nations.keys())
        
        for i in range(len(nation_ids)):
            for j in range(i + 1, len(nation_ids)):
                relation = DiplomaticRelation(
                    nation_a=nation_ids[i],
                    nation_b=nation_ids[j],
                    hatred=40
                )
                game_state.diplomatic_relations.append(relation)
    
    def get_relation_level(self, hatred: int) -> str:
        if hatred > 80:
            return "hostile"
        elif hatred > 50:
            return "tense"
        elif hatred > 30:
            return "neutral"
        elif hatred > 10:
            return "friendly"
        else:
            return "alliance"
    
    def update_relations(self, game_state: GameState):
        for relation in game_state.diplomatic_relations:
            nation_a = game_state.nations.get(relation.nation_a)
            nation_b = game_state.nations.get(relation.nation_b)
            
            if not nation_a or not nation_b:
                continue
            
            if nation_a.ai_type.value == "deepseek" and nation_b.ai_type.value == "aliyun":
                relation.hatred += 1
            elif nation_a.ai_type.value == "aliyun" and nation_b.ai_type.value == "deepseek":
                relation.hatred += 1
            
            relation.hatred = max(0, min(100, relation.hatred))
    
    def perform_diplomatic_action(self, actor: Nation, target: Nation, action: str, game_state: GameState) -> bool:
        relation = game_state.get_relation(actor.id, target.id)
        
        if not relation:
            return False
        
        if action == "trade":
            if relation.hatred < 30:
                relation.trade_agreement = True
                return True
        
        elif action == "alliance":
            if relation.hatred < 10:
                relation.alliance = True
                return True
        
        elif action == "condemn":
            actor.attributes.prestige += 5
            relation.hatred += 10
            return True
        
        elif action == "sanction":
            if actor.resources.food >= 20:
                actor.resources.food -= 20
                return True
        
        elif action == "religious_output":
            if actor.ai_type.value == "kimi" and actor.resources.food >= 30:
                actor.resources.food -= 30
                target.attributes.cohesion -= 3
                return True
        
        return False
    
    def check_diplomatic_events(self, game_state: GameState) -> List[Dict]:
        events = []
        
        for nation_id, nation in game_state.nations.items():
            if nation.ai_type.value == "deepseek" and nation.attributes.prestige > 120:
                if random.random() < 0.05:
                    events.append({
                        "type": "peace_initiative",
                        "nation": nation_id,
                        "description": f"{nation.name} 提议所有国家停战6个月"
                    })
            
            elif nation.ai_type.value == "aliyun" and nation.attributes.military > 15:
                if random.random() < 0.05:
                    target_id = random.choice([n for n in game_state.nations.keys() if n != nation_id])
                    events.append({
                        "type": "war_threat",
                        "nation": nation_id,
                        "target": target_id,
                        "description": f"{nation.name} 向邻国发出最后通牒"
                    })
            
            elif nation.ai_type.value == "kimi" and nation.attributes.cohesion > 20:
                if random.random() < 0.05:
                    target_id = random.choice([n for n in game_state.nations.keys() if n != nation_id])
                    events.append({
                        "type": "religious_infiltration",
                        "nation": nation_id,
                        "target": target_id,
                        "description": f"{nation.name} 的传教士渗透到邻国"
                    })
        
        return events
