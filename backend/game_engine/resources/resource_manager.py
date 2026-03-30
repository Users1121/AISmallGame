from typing import Dict
from models.entities import Nation, GameState


class ResourceManager:
    def __init__(self):
        pass
    
    def _apply_dynamic_balance(self, nation: Nation):
        nation.food_growth_modifier = 1.0
        nation.energy_growth_modifier = 1.0
        nation.economy_growth_modifier = 1.0
        
        food = nation.resources.food
        energy = nation.resources.energy
        economy = nation.resources.economy
        
        threshold = (energy + economy) / 6
        if food < threshold:
            nation.food_growth_modifier = 1.2
            nation.energy_growth_modifier = 0.9
            nation.economy_growth_modifier = 0.9
            return
        
        threshold = (food + economy) / 6
        if energy < threshold:
            nation.energy_growth_modifier = 1.2
            nation.food_growth_modifier = 0.9
            nation.economy_growth_modifier = 0.9
            return
        
        threshold = (food + energy) / 6
        if economy < threshold:
            nation.economy_growth_modifier = 1.2
            nation.food_growth_modifier = 0.9
            nation.energy_growth_modifier = 0.9
            return
    
    def process_monthly_resources(self, nation: Nation) -> Dict[str, int]:
        if not hasattr(nation, 'initial_energy') or nation.initial_energy == 0:
            nation.initial_energy = nation.resources.energy
        if not hasattr(nation, 'initial_economy') or nation.initial_economy == 0:
            nation.initial_economy = nation.resources.economy
        
        self._apply_dynamic_balance(nation)
        
        gain = nation.calculate_resource_gain()
        consumption = nation.calculate_resource_consumption()
        
        total_resources = nation.resources.food + nation.resources.energy + nation.resources.economy
        is_prosperous = total_resources > 100000
        
        energy_economy_sum = nation.resources.energy + nation.resources.economy
        if energy_economy_sum > 40000:
            energy_to_food = int(nation.resources.energy * 0.05)
            economy_to_food = int(nation.resources.economy * 0.05)
            nation.resources.energy -= energy_to_food
            nation.resources.economy -= economy_to_food
            nation.resources.food += energy_to_food + economy_to_food
        
        food_net_change = gain.food - consumption.food

        has_food_buffer = nation.resources.food > nation.population * 1.5
        if has_food_buffer:
            food_growth_rate = 1.0
        else:
            food_growth_rate = food_net_change / max(1, consumption.food)
            food_growth_rate = max(-1.0, min(1.0, food_growth_rate))

        energy_change = int(gain.energy * food_growth_rate) - consumption.energy
        economy_change = gain.economy - consumption.economy

        nation.resources.food += food_net_change
        nation.resources.energy = max(0, nation.resources.energy + energy_change)
        nation.resources.economy = max(0, nation.resources.economy + economy_change)

        return {"food": food_net_change, "energy": energy_change, "economy": economy_change}
    
    def process_population_death(self, nation: Nation) -> Dict:
        death_info = {
            "natural_death": 0,
            "starvation_death": 0,
            "total_death": 0
        }
        
        natural_death = int(nation.population * nation.death_rate)
        death_info["natural_death"] = natural_death
        
        if nation.resources.food < nation.population:
            starvation_death_rate = 0.05
            starvation_death = int(nation.population * starvation_death_rate)
            death_info["starvation_death"] = starvation_death
        else:
            starvation_death = 0
        
        total_death = natural_death + starvation_death
        death_info["total_death"] = total_death
        
        nation.population = max(1, nation.population - total_death)
        
        return death_info
    
    def check_resource_crisis(self, nation: Nation) -> Dict[str, bool]:
        crises = {}
        
        if nation.resources.food < nation.population * 0.8:
            crises["food_shortage"] = True
        else:
            crises["food_shortage"] = False
            
        if nation.resources.energy == 0:
            crises["energy_shortage"] = True
        else:
            crises["energy_shortage"] = False
            
        return crises
    
    def apply_crisis_effects(self, nation: Nation, crises: Dict[str, bool]):
        if crises.get("food_shortage", False):
            nation.attributes.happiness -= 1
            
        if crises.get("energy_shortage", False):
            nation.attributes.development_speed = 0
        else:
            nation.attributes.development_speed = max(1, nation.attributes.development_speed)
    
    def convert_resources(self, nation: Nation, conversion_type: str) -> bool:
        if conversion_type == "energy_to_food":
            if nation.resources.energy >= 1 and nation.population >= 1:
                nation.resources.energy -= 1
                nation.resources.food += 2
                return True
        elif conversion_type == "energy_to_economy":
            if nation.resources.energy >= 1 and nation.population >= 1:
                nation.resources.energy -= 1
                nation.resources.economy += 1
                return True
        return False
