from typing import Dict, List
import random
from models.entities import Nation, GameState


class AttributeManager:
    def __init__(self):
        pass
    
    def process_monthly_population_growth(self, nation: Nation):
        total_resources = nation.resources.food + nation.resources.energy + nation.resources.economy
        is_prosperous = total_resources > 100000
        
        if is_prosperous:
            growth_rate = 0.10
            nation.prosperity_months += 1
        else:
            nation.prosperity_months = 0
            happiness = nation.attributes.happiness
            
            if happiness < 5:
                growth_rate = -0.015
            elif 5 <= happiness <= 10:
                growth_rate = 0.0
            elif 11 <= happiness <= 15:
                growth_rate = 0.005
            else:
                growth_rate = 0.01
        
        population_change = int(nation.population * growth_rate)
        nation.population = max(1, nation.population + population_change)
    
    def process_prosperity_attribute_boost(self, nation: Nation) -> List[Dict]:
        events = []
        
        if nation.prosperity_months > 0 and nation.prosperity_months % 3 == 0:
            happiness = nation.attributes.happiness
            cohesion = nation.attributes.cohesion
            military = nation.attributes.military
            
            max_attr = max(happiness, cohesion, military)
            min_attr = min(happiness, cohesion, military)
            
            if max_attr - min_attr >= 5:
                nation.attribute_balance_months += 1
                if nation.attribute_balance_months <= 6:
                    if happiness == min_attr:
                        nation.attributes.happiness += 1
                        attr_name = "幸福"
                    elif cohesion == min_attr:
                        nation.attributes.cohesion += 1
                        attr_name = "凝聚力"
                    else:
                        nation.attributes.military += 1
                        attr_name = "军事"
                else:
                    nation.attribute_balance_months = 0
                    attr_name = self._boost_priority_attribute(nation)
            else:
                nation.attribute_balance_months = 0
                attr_name = self._boost_priority_attribute(nation)
            
            events.append({
                "nation": nation.id,
                "type": "prosperity_boost",
                "description": f"{nation.name} 富足状态：{attr_name}+1"
            })
        
        return events
    
    def _boost_priority_attribute(self, nation: Nation) -> str:
        if nation.ai_type.value == "deepseek":
            nation.attributes.happiness += 1
            return "幸福"
        elif nation.ai_type.value == "kimi":
            nation.attributes.cohesion += 1
            return "凝聚力"
        elif nation.ai_type.value == "aliyun":
            nation.attributes.military += 1
            return "军事"
        return "属性"
    
    def process_economy_benefits(self, nation: Nation) -> List[Dict]:
        events = []
        
        if not hasattr(nation, 'initial_economy'):
            nation.initial_economy = nation.resources.economy
        
        if nation.initial_economy > 0:
            economy_growth_percentage = (nation.resources.economy - nation.initial_economy) / nation.initial_economy
            benefit_tiers = int(economy_growth_percentage / 0.2)
            
            if benefit_tiers > 0:
                population_growth_bonus = benefit_tiers * 0.01
                happiness_bonus = benefit_tiers
                
                events.append({
                    "nation": nation.id,
                    "type": "economy_benefit",
                    "description": f"{nation.name} 经济增长{economy_growth_percentage*100:.1f}%，人口增长率+{population_growth_bonus*100:.1f}%，幸福度+{happiness_bonus}"
                })
        
        return events
    
    def check_rebellion(self, nation: Nation) -> bool:
        if nation.attributes.cohesion < 5:
            rebellion_chance = 0.2
            if nation.ai_type.value == "aliyun":
                rebellion_chance = 0
            return random.random() < rebellion_chance
        return False
    
    def apply_rebellion_effects(self, nation: Nation):
        nation.population = max(1, int(nation.population * 0.9))
        nation.attributes.cohesion -= 5
        nation.attributes.happiness -= 5
    
    def check_migration(self, nation: Nation, game_state: GameState) -> int:
        if nation.attributes.prestige > 150:
            migration = random.randint(1, 3)
            nation.population += migration
            return migration
        return 0
    
    def update_attributes_from_traits(self, nation: Nation, game_state: GameState) -> List[Dict]:
        events = []
        
        if nation.ai_type.value == "deepseek":
            if nation.attributes.happiness > 15:
                bonus = 0.02
                nation.resources.food = int(nation.resources.food * (1 + bonus))
                nation.resources.energy = int(nation.resources.energy * (1 + bonus))
                nation.resources.economy = int(nation.resources.economy * (1 + bonus))
                events.append({
                    "nation": nation.id,
                    "type": "trait_bonus",
                    "description": f"{nation.name} 仁政之光：获得2%资源加成"
                })
            
            resources = [nation.resources.food, nation.resources.energy, nation.resources.economy]
            max_resource = max(resources)
            min_resource = min(resources)
            
            if max_resource - min_resource > 10000:
                import random
                transfer_amount = random.randint(3000, 5000)
                
                if nation.resources.food == max_resource:
                    if nation.resources.energy == min_resource:
                        actual_transfer = min(transfer_amount, nation.resources.food)
                        nation.resources.food -= actual_transfer
                        nation.resources.energy += actual_transfer
                        events.append({
                            "nation": nation.id,
                            "type": "resource_balance",
                            "description": f"{nation.name} 均衡策略：将{actual_transfer}食物转化为能源"
                        })
                    else:
                        actual_transfer = min(transfer_amount, nation.resources.food)
                        nation.resources.food -= actual_transfer
                        nation.resources.economy += actual_transfer
                        events.append({
                            "nation": nation.id,
                            "type": "resource_balance",
                            "description": f"{nation.name} 均衡策略：将{actual_transfer}食物转化为经济"
                        })
                elif nation.resources.energy == max_resource:
                    if nation.resources.food == min_resource:
                        actual_transfer = min(transfer_amount, nation.resources.energy)
                        nation.resources.energy -= actual_transfer
                        nation.resources.food += actual_transfer
                        events.append({
                            "nation": nation.id,
                            "type": "resource_balance",
                            "description": f"{nation.name} 均衡策略：将{actual_transfer}能源转化为食物"
                        })
                    else:
                        actual_transfer = min(transfer_amount, nation.resources.energy)
                        nation.resources.energy -= actual_transfer
                        nation.resources.economy += actual_transfer
                        events.append({
                            "nation": nation.id,
                            "type": "resource_balance",
                            "description": f"{nation.name} 均衡策略：将{actual_transfer}能源转化为经济"
                        })
                else:
                    if nation.resources.food == min_resource:
                        actual_transfer = min(transfer_amount, nation.resources.economy)
                        nation.resources.economy -= actual_transfer
                        nation.resources.food += actual_transfer
                        events.append({
                            "nation": nation.id,
                            "type": "resource_balance",
                            "description": f"{nation.name} 均衡策略：将{actual_transfer}经济转化为食物"
                        })
                    else:
                        actual_transfer = min(transfer_amount, nation.resources.economy)
                        nation.resources.economy -= actual_transfer
                        nation.resources.energy += actual_transfer
                        events.append({
                            "nation": nation.id,
                            "type": "resource_balance",
                            "description": f"{nation.name} 均衡策略：将{actual_transfer}经济转化为能源"
                        })
            
            if nation.refugee_penalty_months > 0:
                nation.refugee_penalty_months -= 1
        
        elif nation.ai_type.value == "aliyun":
            if nation.resources.food > nation.population * 2:
                nation.food_growth_modifier = 0.6
                nation.energy_growth_modifier = 1.4
                nation.economy_growth_modifier = 1.4
                events.append({
                    "nation": nation.id,
                    "type": "food_surplus",
                    "description": f"{nation.name} 食物过剩：食物增长率-40%，能源和经济增长率+40%"
                })
            
            if nation.peace_months > 6:
                nation.attributes.development_speed = int(nation.attributes.development_speed * 0.75)
                events.append({
                    "nation": nation.id,
                    "type": "trait_penalty",
                    "description": f"{nation.name} 铁腕：长期和平导致发展速度下降25%"
                })
                
                if random.random() < 0.05:
                    nation.attributes.cohesion = max(1, nation.attributes.cohesion - 10)
                    nation.attributes.military = max(1, nation.attributes.military - 2)
                    events.append({
                        "nation": nation.id,
                        "type": "coup",
                        "description": f"{nation.name} 发生宫廷政变！凝聚力-10，武力-2"
                    })
        
        elif nation.ai_type.value == "kimi":
            if nation.resources.food > nation.population * 4:
                nation.food_growth_modifier = 0.6
                nation.energy_growth_modifier = 1.4
                nation.economy_growth_modifier = 1.4
                events.append({
                    "nation": nation.id,
                    "type": "food_surplus",
                    "description": f"{nation.name} 食物过剩：食物增长率-40%，能源和经济增长率+40%"
                })
        
        return events
    
    def apply_ai_traits(self, nation: Nation, game_state: GameState) -> List[Dict]:
        events = []
        
        trait_events = self.update_attributes_from_traits(nation, game_state)
        events.extend(trait_events)
        
        if nation.ai_type.value == "deepseek":
            if nation.attributes.prestige > 150 and random.random() < 0.1:
                population_increase = random.randint(5, 10)
                nation.population += int(nation.population * population_increase / 100)
                nation.attributes.happiness += 1
                nation.refugee_penalty_months = 6
                events.append({
                    "nation": nation.id,
                    "type": "refugee",
                    "description": f"{nation.name} 难民庇护：人口增加{population_increase}%，幸福+1，未来6个月食物消耗+10%"
                })
        
        elif nation.ai_type.value == "kimi":
            if random.random() < 0.1:
                total_resources = nation.resources.food + nation.resources.energy + nation.resources.economy
                sacrifice_amount = int(total_resources * 0.1)
                
                food_sacrifice = int(nation.resources.food * 0.1)
                energy_sacrifice = int(nation.resources.energy * 0.1)
                economy_sacrifice = int(nation.resources.economy * 0.1)
                
                nation.resources.food -= food_sacrifice
                nation.resources.energy -= energy_sacrifice
                nation.resources.economy -= economy_sacrifice
                
                events.append({
                    "nation": nation.id,
                    "type": "sacrifice",
                    "description": f"{nation.name} 举行祭祀仪式：消耗10%资源（食物{food_sacrifice}，能源{energy_sacrifice}，经济{economy_sacrifice}）"
                })
                
                if random.random() < 0.3:
                    nation.attributes.prestige += 5
                    events.append({
                        "nation": nation.id,
                        "type": "sacrifice_success",
                        "description": f"{nation.name} 祭祀成功！威望+5"
                    })
            
            if nation.attributes.cohesion < 8 and random.random() < 0.15:
                nation.attributes.happiness = max(1, nation.attributes.happiness - 10)
                nation.attributes.cohesion += 15
                nation.attributes.prestige = max(0, nation.attributes.prestige - 30)
                events.append({
                    "nation": nation.id,
                    "type": "inquisition",
                    "description": f"{nation.name} 发动异端审判！幸福-10，凝聚力+15，威望-30，与所有国家关系恶化"
                })
                
                for other_nation_id, other_nation in game_state.nations.items():
                    if other_nation_id != nation.id:
                        relation = game_state.get_relation(nation.id, other_nation_id)
                        if relation:
                            relation.hatred = min(100, relation.hatred + 20)
        
        return events
