import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.entities import Nation, AIType, ResourceType, Attributes, TechTree
from game_engine.resources.resource_manager import ResourceManager
from game_engine.resources.attribute_manager import AttributeManager

def test_resource_priority_threshold():
    print("=== 测试资源优先级阈值修改 ===")
    nation = Nation(
        id="test_nation",
        name="测试国家",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=14000, energy=20000, economy=20000),
        attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    resource_manager = ResourceManager()
    
    print(f"初始状态: 人口={nation.population}, 食物={nation.resources.food}")
    print(f"阈值测试: 人口 × 1.5 = {nation.population * 1.5}")
    print(f"食物是否 > 人口 × 1.5: {nation.resources.food > nation.population * 1.5}")
    
    result = resource_manager.process_monthly_resources(nation)
    print(f"资源变化: {result}")
    print(f"处理后: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print()

def test_energy_production_coefficient():
    print("=== 测试能源产出系数修改 ===")
    nation = Nation(
        id="test_nation",
        name="测试国家",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=20000, energy=20000, economy=20000),
        attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    gain = nation.calculate_resource_gain()
    print(f"劳动力: {nation.calculate_labor_force()}")
    print(f"有效领土: {nation.calculate_effective_territory()}")
    print(f"食物产出: {gain.food}")
    print(f"能源产出: {gain.energy}")
    print(f"经济产出: {gain.economy}")
    print(f"能源/食物比例: {gain.energy / gain.food:.2f}")
    print()

def test_resource_conversion():
    print("=== 测试资源转化机制 ===")
    nation = Nation(
        id="test_nation",
        name="测试国家",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=20000, energy=25000, economy=25000),
        attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    resource_manager = ResourceManager()
    
    print(f"初始资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print(f"能源+经济总和: {nation.resources.energy + nation.resources.economy}")
    print(f"是否 > 40000: {nation.resources.energy + nation.resources.economy > 40000}")
    
    result = resource_manager.process_monthly_resources(nation)
    print(f"处理后资源: 食物={nation.resources.food}, 能源={nation.resources.energy}, 经济={nation.resources.economy}")
    print()

def test_prosperity_state():
    print("=== 测试富足状态机制 ===")
    nation = Nation(
        id="test_nation",
        name="测试国家",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=40000, energy=40000, economy=40000),
        attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    attribute_manager = AttributeManager()
    
    total_resources = nation.resources.food + nation.resources.energy + nation.resources.economy
    print(f"总资源: {total_resources}")
    print(f"是否 > 100000: {total_resources > 100000}")
    
    initial_population = nation.population
    attribute_manager.process_monthly_population_growth(nation)
    print(f"人口增长: {initial_population} -> {nation.population}")
    print(f"增长率: {(nation.population - initial_population) / initial_population * 100:.1f}%")
    print(f"富足月数: {nation.prosperity_months}")
    print()

def test_prosperity_attribute_boost():
    print("=== 测试富足状态属性提升机制 ===")
    
    nations = {
        "deepseek": Nation(
            id="deepseek",
            name="DeepSeek·仁心",
            ai_type=AIType.DEEPSEEK,
            resources=ResourceType(food=40000, energy=40000, economy=40000),
            attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
            tech_tree=TechTree(),
            population=10000,
            territory=100.0,
            livability_coefficient=0.8
        ),
        "kimi": Nation(
            id="kimi",
            name="Kimi·神谕",
            ai_type=AIType.KIMI,
            resources=ResourceType(food=40000, energy=40000, economy=40000),
            attributes=Attributes(happiness=10, cohesion=14, military=11, prestige=90, development_speed=9),
            tech_tree=TechTree(),
            population=10000,
            territory=100.0,
            livability_coefficient=0.6
        ),
        "aliyun": Nation(
            id="aliyun",
            name="阿里云百炼·铁腕",
            ai_type=AIType.ALIYUN,
            resources=ResourceType(food=40000, energy=40000, economy=40000),
            attributes=Attributes(happiness=8, cohesion=9, military=12, prestige=100, development_speed=11),
            tech_tree=TechTree(),
            population=10000,
            territory=100.0,
            livability_coefficient=0.5
        )
    }
    
    attribute_manager = AttributeManager()
    
    for nation_id, nation in nations.items():
        print(f"\n{nation.name}:")
        print(f"  初始属性: 幸福={nation.attributes.happiness}, 凝聚力={nation.attributes.cohesion}, 军事={nation.attributes.military}")
        
        for month in range(1, 7):
            nation.prosperity_months = month
            events = attribute_manager.process_prosperity_attribute_boost(nation)
            if events:
                print(f"  第{month}个月: {events[0]['description']}")
        
        print(f"  最终属性: 幸福={nation.attributes.happiness}, 凝聚力={nation.attributes.cohesion}, 军事={nation.attributes.military}")
    print()

def test_resource_consumption():
    print("=== 测试资源消耗机制 ===")
    
    normal_nation = Nation(
        id="normal",
        name="正常状态国家",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=20000, energy=20000, economy=20000),
        attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    prosperous_nation = Nation(
        id="prosperous",
        name="富足状态国家",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=40000, energy=40000, economy=40000),
        attributes=Attributes(happiness=13, cohesion=13, military=10, prestige=115, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100.0,
        livability_coefficient=0.8
    )
    
    normal_consumption = normal_nation.calculate_resource_consumption()
    prosperous_consumption = prosperous_nation.calculate_resource_consumption()
    
    print(f"正常状态消耗: 食物={normal_consumption.food}, 能源={normal_consumption.energy}, 经济={normal_consumption.economy}")
    print(f"富足状态消耗: 食物={prosperous_consumption.food}, 能源={prosperous_consumption.energy}, 经济={prosperous_consumption.economy}")
    print(f"正常状态能源消耗占食物消耗: {normal_consumption.energy / normal_consumption.food * 100:.0f}%")
    print(f"富足状态能源消耗占食物消耗: {prosperous_consumption.energy / prosperous_consumption.food * 100:.0f}%")
    print(f"富足状态能源消耗是正常的: {prosperous_consumption.energy / normal_consumption.energy:.1f}倍")
    print()

if __name__ == "__main__":
    test_resource_priority_threshold()
    test_energy_production_coefficient()
    test_resource_conversion()
    test_prosperity_state()
    test_prosperity_attribute_boost()
    test_resource_consumption()
    
    print("=== 所有测试完成 ===")
