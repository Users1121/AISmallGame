from typing import Dict, List, Optional
from models.entities import Nation, GameState
from pydantic import BaseModel


class HistoricalExperience(BaseModel):
    target_nation: str
    attack_attempts: int = 0
    intervention_failures: Dict[str, int] = {}
    success_rate: float = 0.0
    last_attack_month: int = 0


class HistoricalExperienceManager:
    def __init__(self):
        self.experience_data: Dict[str, Dict[str, HistoricalExperience]] = {}
    
    def record_war_outcome(self, attacker_id: str, defender_id: str, 
                          interveners: List[str], attacker_won: bool, 
                          game_state: GameState):
        if attacker_id not in self.experience_data:
            self.experience_data[attacker_id] = {}
        
        if defender_id not in self.experience_data[attacker_id]:
            self.experience_data[attacker_id][defender_id] = HistoricalExperience(
                target_nation=defender_id
            )
        
        experience = self.experience_data[attacker_id][defender_id]
        experience.attack_attempts += 1
        experience.last_attack_month = game_state.current_year * 12 + game_state.current_month
        
        if not attacker_won and interveners:
            for intervener_id in interveners:
                if intervener_id not in experience.intervention_failures:
                    experience.intervention_failures[intervener_id] = 0
                experience.intervention_failures[intervener_id] += 1
        
        total_attempts = experience.attack_attempts
        success_count = 0
        if attacker_won:
            success_count = 1
        
        experience.success_rate = (experience.success_rate * (total_attempts - 1) + success_count) / total_attempts
    
    def get_experience(self, nation_id: str, target_id: str) -> Optional[HistoricalExperience]:
        if nation_id in self.experience_data and target_id in self.experience_data[nation_id]:
            return self.experience_data[nation_id][target_id]
        return None
    
    def should_avoid_target(self, nation_id: str, target_id: str) -> bool:
        experience = self.get_experience(nation_id, target_id)
        if not experience:
            return False
        
        if experience.attack_attempts >= 2 and experience.success_rate < 0.5:
            return True
        
        return False
    
    def get_intervention_threat(self, nation_id: str, potential_target: str, 
                               game_state: GameState) -> Dict[str, float]:
        experience = self.get_experience(nation_id, potential_target)
        if not experience:
            return {}
        
        threat_levels = {}
        for intervener_id, failure_count in experience.intervention_failures.items():
            if failure_count >= 2:
                relation = game_state.get_relation(nation_id, intervener_id)
                if relation:
                    base_threat = 0.7
                    if relation.hatred > 50:
                        base_threat += 0.2
                    threat_levels[intervener_id] = min(1.0, base_threat)
        
        return threat_levels
    
    def get_strategic_recommendation(self, nation_id: str, game_state: GameState) -> Dict:
        if nation_id not in self.experience_data:
            return {"action": "normal", "reason": "无历史经验"}
        
        experiences = self.experience_data[nation_id]
        recommendation = {"action": "normal", "reason": "正常决策"}
        
        for target_id, experience in experiences.items():
            if self.should_avoid_target(nation_id, target_id):
                threat_levels = self.get_intervention_threat(nation_id, target_id, game_state)
                
                if threat_levels:
                    highest_threat = max(threat_levels.items(), key=lambda x: x[1])
                    if highest_threat[1] > 0.8:
                        recommendation = {
                            "action": "punitive_strike",
                            "target": highest_threat[0],
                            "reason": f"历史上{highest_threat[0]}多次干预对{target_id}的攻击，建议先对其发动惩戒性攻击"
                        }
                        break
        
        return recommendation
    
    def get_attack_priority(self, nation_id: str, game_state: GameState) -> List[Dict]:
        if nation_id not in self.experience_data:
            return []
        
        experiences = self.experience_data[nation_id]
        priorities = []
        
        for target_id, experience in experiences.items():
            target_nation = game_state.nations.get(target_id)
            if not target_nation:
                continue
            
            priority_score = 0
            
            if experience.success_rate > 0.7:
                priority_score += 30
            
            if experience.attack_attempts >= 2 and not experience.intervention_failures:
                priority_score += 20
            
            if self.should_avoid_target(nation_id, target_id):
                priority_score -= 40
            
            priorities.append({
                "target_id": target_id,
                "priority_score": priority_score,
                "success_rate": experience.success_rate,
                "attempts": experience.attack_attempts
            })
        
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities