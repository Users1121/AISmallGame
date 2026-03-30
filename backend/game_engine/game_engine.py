from typing import Dict, List
import random
from models.entities import Nation, GameState
from game_engine.resources.resource_manager import ResourceManager
from game_engine.resources.attribute_manager import AttributeManager
from game_engine.events.event_manager import EventManager
from game_engine.war.war_manager import WarManager
from game_engine.diplomacy.diplomacy_manager import DiplomacyManager
from game_engine.ending.ending_manager import EndingManager
from game_engine.ending.ending_storage import EndingStorage


class GameEngine:
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.attribute_manager = AttributeManager()
        self.event_manager = EventManager()
        self.war_manager = WarManager()
        self.diplomacy_manager = DiplomacyManager()
        self.ending_manager = EndingManager()
        self.ending_storage = EndingStorage()
    
    def initialize_game(self, game_state: GameState):
        self.diplomacy_manager.initialize_relations(game_state)
    
    def process_month(self, game_state: GameState) -> Dict:
        results = {
            "month": game_state.current_month,
            "year": game_state.current_year,
            "events": [],
            "resource_changes": {},
            "attribute_changes": {},
            "wars": [],
            "diplomatic_events": []
        }
        
        for nation_id, nation in game_state.nations.items():
            nation_results = self._process_nation_month(nation, game_state)
            results["resource_changes"][nation_id] = nation_results["resource_changes"]
            results["attribute_changes"][nation_id] = nation_results["attribute_changes"]
            results["events"].extend(nation_results["events"])
        
        self.diplomacy_manager.update_relations(game_state)
        diplomatic_events = self.diplomacy_manager.check_diplomatic_events(game_state)
        results["diplomatic_events"] = diplomatic_events
        
        self._check_deepseek_humanitarian_aid(game_state, results)
        
        self._check_aliyun_food_crisis_war(game_state, results)
        
        self._process_wars(game_state, results)
        
        month_summary = f"{game_state.current_year}年{game_state.current_month}月"
        if len(results["events"]) == 0 and len(results["wars"]) == 0 and len(diplomatic_events) == 0:
            game_state.event_history.append(f"{month_summary}：各个国家相安无事")
        else:
            game_state.event_history.append(f"{month_summary}")
            for event in results["events"]:
                if isinstance(event, dict) and "description" in event:
                    game_state.event_history.append(f"  - {event['description']}")
            for war in results["wars"]:
                if "winner" in war and "loser" in war:
                    game_state.event_history.append(f"  - {war['winner']} 击败了 {war['loser']}")
            for dip_event in diplomatic_events:
                if isinstance(dip_event, dict) and "description" in dip_event:
                    game_state.event_history.append(f"  - {dip_event['description']}")
        
        game_state.advance_time()
        
        ending = self.ending_manager.check_endings(game_state)
        if ending:
            game_state.ending_triggered = True
            game_state.ending_data = ending
            results["ending"] = ending
        
        return results
    
    def _process_nation_month(self, nation: Nation, game_state: GameState) -> Dict:
        results = {
            "resource_changes": {},
            "attribute_changes": {},
            "events": []
        }
        
        resource_changes = self.resource_manager.process_monthly_resources(nation)
        results["resource_changes"] = resource_changes
        
        crises = self.resource_manager.check_resource_crisis(nation)
        self.resource_manager.apply_crisis_effects(nation, crises)
        
        self.attribute_manager.process_monthly_population_growth(nation)
        
        death_info = self.resource_manager.process_population_death(nation)
        if death_info["starvation_death"] > 0:
            results["events"].append({
                "nation": nation.id,
                "type": "starvation",
                "description": f"{nation.name} 因粮食不足，本月死亡 {death_info['starvation_death']} 人"
            })
        
        if self.attribute_manager.check_rebellion(nation):
            self.attribute_manager.apply_rebellion_effects(nation)
            results["events"].append({
                "nation": nation.id,
                "type": "rebellion",
                "description": f"{nation.name} 发生了内部叛乱"
            })
        
        migration = self.attribute_manager.check_migration(nation, game_state)
        if migration > 0:
            results["events"].append({
                "nation": nation.id,
                "type": "migration",
                "description": f"{nation.name} 接收了 {migration} 名移民"
            })
        
        ai_trait_events = self.attribute_manager.apply_ai_traits(nation, game_state)
        results["events"].extend(ai_trait_events)
        
        prosperity_events = self.attribute_manager.process_prosperity_attribute_boost(nation)
        results["events"].extend(prosperity_events)
        
        if self.event_manager.check_event_trigger():
            event = self.event_manager.trigger_random_event(nation)
            results["events"].append({
                "nation": nation.id,
                "type": "random_event",
                "event": event,
                "description": f"{nation.name} 遭遇随机事件「{event.get('name', '未知事件')}」：{event.get('description', '')}"
            })
        
        return results
    
    def _process_wars(self, game_state: GameState, results: Dict):
        active_wars = [war for war in game_state.active_wars if war.is_active]
        
        for war in active_wars:
            attacker = game_state.nations.get(war.attacker)
            defender = game_state.nations.get(war.defender)
            
            if not attacker or not defender:
                continue
            
            interveners = self.war_manager.check_third_party_intervention(war, game_state)
            
            war_result = self.war_manager.resolve_war(war, attacker, defender)
            results["wars"].append(war_result)
    
    def _check_deepseek_humanitarian_aid(self, game_state: GameState, results: Dict):
        for nation_id, nation in game_state.nations.items():
            if nation.ai_type.value != "deepseek":
                continue
            
            if nation.resources.food < nation.population * 2:
                continue
            
            for other_id, other_nation in game_state.nations.items():
                if other_id == nation.id:
                    continue
                
                if other_nation.resources.food < other_nation.population:
                    if random.random() < 0.3:
                        population_transfer = int(other_nation.population * 0.03)
                        prestige_gain = 15
                        
                        other_nation.population -= population_transfer
                        nation.population += population_transfer
                        nation.attributes.prestige += prestige_gain
                        
                        results["events"].append({
                            "nation": nation.id,
                            "type": "humanitarian_aid",
                            "description": f"{nation.name} 向 {other_nation.name} 提供人道主义援助，接收 {population_transfer} 人，威望+15"
                        })
                        break
    
    def _check_aliyun_food_crisis_war(self, game_state: GameState, results: Dict):
        for nation_id, nation in game_state.nations.items():
            if nation.ai_type.value != "aliyun":
                continue
            
            if nation.resources.food < nation.population:
                potential_targets = []
                
                for target_id, target_nation in game_state.nations.items():
                    if target_id == nation_id:
                        continue
                    
                    existing_war = any(
                        (war.attacker == nation_id and war.defender == target_id) or
                        (war.attacker == target_id and war.defender == nation_id)
                        for war in game_state.active_wars
                    )
                    
                    if not existing_war and target_nation.attributes.military < nation.attributes.military * 0.8:
                        potential_targets.append(target_nation)
                
                if potential_targets:
                    target = random.choice(potential_targets)
                    if self.war_manager.can_declare_war(nation, target):
                        war = self.war_manager.declare_war(nation, target, game_state)
                        results["events"].append({
                            "nation": nation.id,
                            "type": "food_crisis_war",
                            "description": f"{nation.name} 因粮食不足发动掠夺战争，侵略 {target.name}"
                        })
    
    def handle_player_action(self, game_state: GameState, action: Dict) -> Dict:
        action_type = action.get("action_type")
        target_nation_id = action.get("target_nation")
        parameters = action.get("parameters", {})
        
        if action_type == "declare_war":
            attacker = game_state.nations.get(parameters.get("attacker_id"))
            defender = game_state.nations.get(target_nation_id)
            
            if attacker and defender:
                if self.war_manager.can_declare_war(attacker, defender):
                    war = self.war_manager.declare_war(attacker, defender, game_state)
                    return {"success": True, "message": "战争已宣战"}
                else:
                    return {"success": False, "message": "不满足宣战条件"}
        
        elif action_type == "diplomatic_action":
            actor = game_state.nations.get(parameters.get("actor_id"))
            target = game_state.nations.get(target_nation_id)
            
            if actor and target:
                diplomatic_action = parameters.get("action")
                success = self.diplomacy_manager.perform_diplomatic_action(
                    actor, target, diplomatic_action, game_state
                )
                return {"success": success, "message": "外交行动已执行"}
        
        elif action_type == "convert_resources":
            nation = game_state.nations.get(parameters.get("nation_id"))
            if nation:
                conversion_type = parameters.get("conversion_type")
                success = self.resource_manager.convert_resources(nation, conversion_type)
                return {"success": success, "message": "资源转换已执行"}
        
        elif action_type == "god_intervention":
            return self._handle_god_intervention(game_state, parameters)
        
        return {"success": False, "message": "未知操作"}
    
    def _handle_god_intervention(self, game_state: GameState, parameters: Dict) -> Dict:
        intervention_type = parameters.get("type")
        
        if intervention_type == "disaster":
            target_nation = game_state.nations.get(parameters.get("target_nation"))
            if target_nation:
                disaster_type = parameters.get("disaster_type", "radiation_storm")
                
                if disaster_type == "radiation_storm":
                    target_nation.resources.food = int(target_nation.resources.food * 0.7)
                    target_nation.resources.energy = int(target_nation.resources.energy * 0.7)
                    target_nation.attributes.happiness -= 3
                elif disaster_type == "plague":
                    target_nation.population = int(target_nation.population * 0.8)
                    target_nation.attributes.happiness -= 5
                
                return {"success": True, "message": "灾难已降临"}
        
        elif intervention_type == "blessing":
            target_nation = game_state.nations.get(parameters.get("target_nation"))
            if target_nation:
                target_nation.resources.food += 100
                target_nation.resources.energy += 100
                target_nation.attributes.happiness += 5
                
                return {"success": True, "message": "祝福已赐予"}
        
        return {"success": False, "message": "未知干预类型"}
    
    def handle_ending_triggered(self, game_state: GameState) -> Dict:
        if game_state.ending_triggered and game_state.ending_data:
            ending_saved = self.ending_storage.save_ending(
                game_state.ending_data,
                game_state.simulation_count,
                game_state
            )
            
            result = {
                "ending_triggered": True,
                "ending_data": game_state.ending_data,
                "simulation_count": game_state.simulation_count,
                "ending_saved": ending_saved
            }
            
            game_state.simulation_count += 1
            
            return result
        
        return {"ending_triggered": False}
