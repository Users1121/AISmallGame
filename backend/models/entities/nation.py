from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum


class AIType(str, Enum):
    DEEPSEEK = "deepseek"
    ALIYUN = "aliyun"
    KIMI = "kimi"


class ResourceType(BaseModel):
    food: int = 0
    energy: int = 0
    economy: int = 0


class Attributes(BaseModel):
    happiness: int = 10
    cohesion: int = 10
    military: int = 10
    prestige: int = 100
    development_speed: int = 10


class TechTree(BaseModel):
    military_level: int = 0
    social_level: int = 0
    exploration_level: int = 0
    military_points: int = 0
    social_points: int = 0
    exploration_points: int = 0


class Nation(BaseModel):
    id: str
    name: str
    ai_type: AIType
    resources: ResourceType
    attributes: Attributes
    tech_tree: TechTree
    population: int = 10000
    territory: float = 100.0
    livability_coefficient: float = 0.5
    refugee_penalty_months: int = 0
    peace_months: int = 0
    war_months: int = 0
    happiness_tolerance: float = 1.0
    resource_expectation: float = 1.0
    death_rate: float = 0.008
    color: str = "#ffffff"
    initial_energy: int = 0
    initial_economy: int = 0
    prosperity_months: int = 0
    attribute_balance_months: int = 0
    food_growth_modifier: float = 1.0
    energy_growth_modifier: float = 1.0
    economy_growth_modifier: float = 1.0
    
    def calculate_labor_force(self) -> int:
        return int(self.population * 0.6)
    
    def calculate_effective_territory(self) -> float:
        return self.territory * self.livability_coefficient
    
    def calculate_resource_gain(self) -> ResourceType:
        labor_force = self.calculate_labor_force()
        effective_territory = self.calculate_effective_territory()
        multiplier = 1 + self.attributes.development_speed * 0.1
        
        food_gain = int(labor_force * 0.8 * multiplier * (effective_territory / 100) * self.food_growth_modifier)
        energy_gain = int(labor_force * 0.4 * (1 + self.attributes.development_speed * 0.15) * (effective_territory / 100) * self.energy_growth_modifier)
        
        economy_growth_rate = (self.population * (0.5 * self.attributes.cohesion + 0.3 * self.attributes.happiness + self.attributes.development_speed)) / 100
        economy_gain = int(economy_growth_rate * self.economy_growth_modifier)
        
        return ResourceType(
            food=food_gain,
            energy=energy_gain,
            economy=economy_gain
        )
    
    def calculate_resource_consumption(self) -> ResourceType:
        food_consumption = int(self.population * 0.5)
        
        if self.refugee_penalty_months > 0:
            food_consumption = int(food_consumption * 1.1)
        
        total_resources = self.resources.food + self.resources.energy + self.resources.economy
        is_prosperous = total_resources > 100000
        
        if is_prosperous:
            energy_consumption = int(food_consumption * 1.0)
            economy_consumption = int(food_consumption * 1.0)
        else:
            energy_consumption = int(food_consumption * 0.4)
            economy_consumption = int(food_consumption * 0.4)
        
        return ResourceType(food=food_consumption, energy=energy_consumption, economy=economy_consumption)
