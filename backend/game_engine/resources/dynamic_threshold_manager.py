from typing import Dict, List
from models.entities import Nation, GameState
from pydantic import BaseModel


class DynamicThresholdManager:
    def __init__(self):
        self.base_happiness_threshold = 5
        self.base_resource_threshold = 0.8
    
    def calculate_dynamic_happiness_threshold(self, nation: Nation, game_state: GameState) -> float:
        base_threshold = self.base_happiness_threshold
        
        total_months = (game_state.current_year - 2048) * 12 + game_state.current_month
        
        if total_months > 24:
            base_threshold -= 0.5
        
        avg_resources = (
            nation.resources.food + nation.resources.energy + nation.resources.economy
        ) / 3
        
        expected_food = nation.population * 0.8 * nation.resource_expectation
        resource_ratio = nation.resources.food / expected_food if expected_food > 0 else 1
        
        if resource_ratio < 0.5:
            base_threshold -= 1.5
        elif resource_ratio < 0.7:
            base_threshold -= 1.0
        elif resource_ratio > 1.2:
            base_threshold += 0.5
        
        if nation.peace_months > 12:
            base_threshold += 1.0
        elif nation.peace_months > 6:
            base_threshold += 0.5
        
        base_threshold *= nation.happiness_tolerance
        
        return max(1, min(15, base_threshold))
    
    def calculate_dynamic_resource_threshold(self, nation: Nation, game_state: GameState) -> float:
        base_threshold = self.base_resource_threshold
        
        total_months = (game_state.current_year - 2048) * 12 + game_state.current_month
        
        if total_months > 36:
            base_threshold += 0.1
        
        if nation.attributes.development_speed > 15:
            base_threshold += 0.15
        
        if nation.peace_months > 12:
            base_threshold += 0.1
        
        base_threshold *= nation.resource_expectation
        
        return min(1.5, base_threshold)
    
    def update_dynamic_expectations(self, nation: Nation, game_state: GameState):
        total_months = (game_state.current_year - 2048) * 12 + game_state.current_month
        
        if total_months > 24:
            recent_resources = self._get_recent_resource_trend(nation, game_state)
            
            if recent_resources["trend"] == "increasing":
                nation.resource_expectation = min(1.5, nation.resource_expectation + 0.05)
            elif recent_resources["trend"] == "stable":
                pass
            else:
                nation.resource_expectation = max(0.7, nation.resource_expectation - 0.05)
        
        if nation.peace_months > 12:
            nation.happiness_tolerance = min(1.5, nation.happiness_tolerance + 0.02)
        elif nation.peace_months < 6:
            nation.happiness_tolerance = max(0.7, nation.happiness_tolerance - 0.02)
    
    def _get_recent_resource_trend(self, nation: Nation, game_state: GameState) -> Dict:
        current_food = nation.resources.food
        expected_food = nation.population * 0.8 * nation.resource_expectation
        
        ratio = current_food / expected_food if expected_food > 0 else 1
        
        if ratio > 1.1:
            return {"trend": "increasing", "ratio": ratio}
        elif ratio > 0.9:
            return {"trend": "stable", "ratio": ratio}
        else:
            return {"trend": "decreasing", "ratio": ratio}
    
    def check_resource_crisis(self, nation: Nation, game_state: GameState) -> Dict[str, bool]:
        dynamic_threshold = self.calculate_dynamic_resource_threshold(nation, game_state)
        
        crises = {}
        
        expected_food = nation.population * 0.8 * dynamic_threshold
        if nation.resources.food < expected_food:
            crises["food_shortage"] = True
        else:
            crises["food_shortage"] = False
        
        if nation.resources.energy == 0:
            crises["energy_shortage"] = True
        else:
            crises["energy_shortage"] = False
        
        return crises
    
    def apply_crisis_effects(self, nation: Nation, crises: Dict[str, bool], game_state: GameState):
        dynamic_threshold = self.calculate_dynamic_happiness_threshold(nation, game_state)
        
        if crises.get("food_shortage", False):
            if nation.attributes.happiness < dynamic_threshold:
                nation.attributes.happiness -= 2
            else:
                nation.attributes.happiness -= 1
        
        if crises.get("energy_shortage", False):
            nation.attributes.development_speed = 0
        else:
            nation.attributes.development_speed = max(1, nation.attributes.development_speed)
    
    def get_population_growth_rate(self, nation: Nation, game_state: GameState) -> float:
        dynamic_threshold = self.calculate_dynamic_happiness_threshold(nation, game_state)
        happiness = nation.attributes.happiness
        
        if happiness < dynamic_threshold:
            return -0.015
        elif happiness < dynamic_threshold + 5:
            return 0.0
        elif happiness < dynamic_threshold + 10:
            return 0.005
        else:
            return 0.01
    
    def get_war_decline_threshold(self, nation: Nation, game_state: GameState) -> float:
        base_threshold = 5.0
        
        if nation.peace_months > 12:
            base_threshold += 1.0
        
        if nation.resource_expectation > 1.2:
            base_threshold += 0.5
        
        return base_threshold
    
    def get_migration_threshold(self, nation: Nation, game_state: GameState) -> int:
        base_threshold = 150
        
        if nation.peace_months > 12:
            base_threshold -= 20
        
        if nation.happiness_tolerance > 1.2:
            base_threshold -= 10
        
        return max(100, base_threshold)