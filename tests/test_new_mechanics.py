import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.entities import Nation, AIType, ResourceType, Attributes, TechTree
from game_engine.resources.resource_manager import ResourceManager
from game_engine.resources.attribute_manager import AttributeManager
from models.entities import GameState

def test_dynamic_balance():
    print("=== 测试动态持恒机制 ===")
    
    nation = Nation(
        id="test_nation",
        name="测试国家",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=5000, energy=20000, economy=20000),
        attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    resource_manager = ResourceManager()
    
    print(f"初始资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print(f"能源+经济总和: {nation.resources.energy + nation.resources.economy}")
    print(f"阈值 (能源+经济)/6: {(nation.resources.energy + nation.resources.economy) / 6}")
    print(f"食物是否 < 阈值: {nation.resources.food < (nation.resources.energy + nation.resources.economy) / 6}")
    
    resource_manager._apply_dynamic_balance(nation)
    
    print(f"食物增长率调整: {nation.food_growth_modifier}")
    print(f"能源增长率调整: {nation.energy_growth_modifier}")
    print(f"经济增长率调整: {nation.economy_growth_modifier}")
    
    gain = nation.calculate_resource_gain()
    print(f"实际产出: 食物={gain.food}, 能源={gain.energy}, 经济={gain.economy}")
    print()

def test_deepseek_balance():
    print("=== 测试DeepSeek均衡策略 ===")
    
    nation = Nation(
        id="deepseek",
        name="DeepSeek·仁心",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=30000, energy=10000, economy=10000),
        attributes=Attributes(happiness=16, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    attribute_manager = AttributeManager()
    game_state = GameState()
    game_state.nations = {"deepseek": nation}
    
    print(f"初始资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print(f"最大最小差异: {max(nation.resources.food, nation.resources.energy, nation.resources.economy) - min(nation.resources.food, nation.resources.energy, nation.resources.economy)}")
    
    events = attribute_manager.update_attributes_from_traits(nation, game_state)
    
    print(f"处理后资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    if events:
        for event in events:
            if event["type"] == "resource_balance":
                print(f"事件: {event['description']}")
    print()

def test_kimi_food_surplus():
    print("=== 测试Kimi食物过剩策略 ===")
    
    nation = Nation(
        id="kimi",
        name="Kimi·神谕",
        ai_type=AIType.KIMI,
        resources=ResourceType(food=50000, energy=20000, economy=20000),
        attributes=Attributes(happiness=10, cohesion=14, military=11, prestige=90, development_speed=9),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.6
    )
    
    attribute_manager = AttributeManager()
    game_state = GameState()
    game_state.nations = {"kimi": nation}
    
    print(f"初始资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print(f"人口 × 4: {nation.population * 4}")
    print(f"食物是否 > 人口×4: {nation.resources.food > nation.population * 4}")
    
    events = attribute_manager.update_attributes_from_traits(nation, game_state)
    
    print(f"食物增长率调整: {nation.food_growth_modifier}")
    print(f"能源增长率调整: {nation.energy_growth_modifier}")
    print(f"经济增长率调整: {nation.economy_growth_modifier}")
    
    if events:
        for event in events:
            if event["type"] == "food_surplus":
                print(f"事件: {event['description']}")
    print()

def test_kimi_sacrifice():
    print("=== 测试Kimi祭祀特性 ===")
    
    nation = Nation(
        id="kimi",
        name="Kimi·神谕",
        ai_type=AIType.KIMI,
        resources=ResourceType(food=30000, energy=30000, economy=30000),
        attributes=Attributes(happiness=10, cohesion=14, military=11, prestige=90, development_speed=9),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.6
    )
    
    attribute_manager = AttributeManager()
    game_state = GameState()
    game_state.nations = {"kimi": nation}
    
    print(f"初始资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print(f"初始威望: {nation.attributes.prestige}")
    
    events = attribute_manager.apply_ai_traits(nation, game_state)
    
    print(f"处理后资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print(f"处理后威望: {nation.attributes.prestige}")
    
    sacrifice_events = [e for e in events if e["type"] in ["sacrifice", "sacrifice_success"]]
    if sacrifice_events:
        for event in sacrifice_events:
            print(f"事件: {event['description']}")
    print()

def test_aliyun_food_surplus():
    print("=== 测试阿里云食物过剩策略 ===")
    
    nation = Nation(
        id="aliyun",
        name="阿里云百炼·铁腕",
        ai_type=AIType.ALIYUN,
        resources=ResourceType(food=25000, energy=20000, economy=20000),
        attributes=Attributes(happiness=8, cohesion=9, military=12, prestige=100, development_speed=11),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.5
    )
    
    attribute_manager = AttributeManager()
    game_state = GameState()
    game_state.nations = {"aliyun": nation}
    
    print(f"初始资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print(f"人口 × 2: {nation.population * 2}")
    print(f"食物是否 > 人口×2: {nation.resources.food > nation.population * 2}")
    
    events = attribute_manager.update_attributes_from_traits(nation, game_state)
    
    print(f"食物增长率调整: {nation.food_growth_modifier}")
    print(f"能源增长率调整: {nation.energy_growth_modifier}")
    print(f"经济增长率调整: {nation.economy_growth_modifier}")
    
    if events:
        for event in events:
            if event["type"] == "food_surplus":
                print(f"事件: {event['description']}")
    print()

if __name__ == "__main__":
    test_dynamic_balance()
    test_deepseek_balance()
    test_kimi_food_surplus()
    test_kimi_sacrifice()
    test_aliyun_food_surplus()
    
    print("=== 所有测试完成 ===")
