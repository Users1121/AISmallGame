import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.entities import GameState, Nation, AIType, ResourceType, Attributes, TechTree
from game_engine.game_engine import GameEngine
from game_engine.ending.ending_manager import EndingManager
from game_engine.ending.ending_storage import EndingStorage


def test_ending_system():
    print("=" * 60)
    print("测试结局系统")
    print("=" * 60)
    
    game_engine = GameEngine()
    ending_manager = EndingManager()
    ending_storage = EndingStorage()
    
    print("\n1. 测试结局一：仁政之光 (DeepSeek)")
    print("-" * 60)
    
    game_state = GameState()
    game_state.current_year = 2055
    game_state.current_month = 6
    
    deepseek = Nation(
        id="nation_a",
        name="DeepSeek·仁心",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=50000, energy=200, parts=200),
        attributes=Attributes(happiness=19, cohesion=15, military=20, prestige=190, development_speed=12),
        tech_tree=TechTree(),
        population=25000,
        territory=250,
        livability_coefficient=0.8,
        color="#4CAF50"
    )
    
    aliyun = Nation(
        id="nation_b",
        name="阿里云百炼·铁腕",
        ai_type=AIType.ALIYUN,
        resources=ResourceType(food=10000, energy=50, parts=50),
        attributes=Attributes(happiness=8, cohesion=9, military=12, prestige=100, development_speed=11),
        tech_tree=TechTree(),
        population=7000,
        territory=70,
        livability_coefficient=0.5,
        color="#F44336"
    )
    
    kimi = Nation(
        id="nation_c",
        name="Kimi·神谕",
        ai_type=AIType.KIMI,
        resources=ResourceType(food=10000, energy=50, parts=50),
        attributes=Attributes(happiness=10, cohesion=14, military=11, prestige=90, development_speed=9),
        tech_tree=TechTree(),
        population=7000,
        territory=70,
        livability_coefficient=0.6,
        color="#9C27B0"
    )
    
    game_state.nations = {
        "nation_a": deepseek,
        "nation_b": aliyun,
        "nation_c": kimi
    }
    
    from models.entities.game_state import DiplomaticRelation
    game_state.diplomatic_relations = [
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_b", hatred=15),
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_c", hatred=18),
        DiplomaticRelation(nation_a="nation_b", nation_b="nation_c", hatred=40)
    ]
    
    ending = ending_manager.check_endings(game_state)
    if ending:
        print(f"✓ 触发结局：{ending['name']}")
        print(f"  获胜者：{ending['winner']}")
        print(f"  描述：{ending['description'][:50]}...")
        
        game_state.ending_triggered = True
        game_state.ending_data = ending
        saved = ending_storage.save_ending(ending, 1, game_state)
        print(f"  保存状态：{'成功' if saved else '失败'}")
    else:
        print("✗ 未触发结局")
    
    print("\n2. 测试结局二：钢铁洪流 (阿里云)")
    print("-" * 60)
    
    game_state2 = GameState()
    game_state2.current_year = 2053
    game_state2.current_month = 9
    
    aliyun2 = Nation(
        id="nation_b",
        name="阿里云百炼·铁腕",
        ai_type=AIType.ALIYUN,
        resources=ResourceType(food=60000, energy=300, parts=300),
        attributes=Attributes(happiness=7, cohesion=4, military=25, prestige=120, development_speed=11),
        tech_tree=TechTree(),
        population=15000,
        territory=180,
        livability_coefficient=0.5,
        color="#F44336"
    )
    
    deepseek2 = Nation(
        id="nation_a",
        name="DeepSeek·仁心",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=10000, energy=50, parts=50),
        attributes=Attributes(happiness=10, cohesion=10, military=10, prestige=100, development_speed=10),
        tech_tree=TechTree(),
        population=8000,
        territory=80,
        livability_coefficient=0.8,
        color="#4CAF50"
    )
    
    kimi2 = Nation(
        id="nation_c",
        name="Kimi·神谕",
        ai_type=AIType.KIMI,
        resources=ResourceType(food=10000, energy=50, parts=50),
        attributes=Attributes(happiness=10, cohesion=10, military=10, prestige=100, development_speed=10),
        tech_tree=TechTree(),
        population=8000,
        territory=80,
        livability_coefficient=0.6,
        color="#9C27B0"
    )
    
    game_state2.nations = {
        "nation_a": deepseek2,
        "nation_b": aliyun2,
        "nation_c": kimi2
    }
    
    game_state2.diplomatic_relations = [
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_b", hatred=85),
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_c", hatred=40),
        DiplomaticRelation(nation_a="nation_b", nation_b="nation_c", hatred=90)
    ]
    
    from models.entities.game_state import WarState
    game_state2.active_wars = [
        WarState(attacker="nation_b", defender="nation_a", start_month=1, end_month=3, is_active=False),
        WarState(attacker="nation_b", defender="nation_c", start_month=4, end_month=6, is_active=False),
        WarState(attacker="nation_b", defender="nation_a", start_month=7, end_month=9, is_active=False)
    ]
    
    aliyun2.peace_months = 0
    aliyun2.war_months = 10
    
    ending2 = ending_manager.check_endings(game_state2)
    if ending2:
        print(f"✓ 触发结局：{ending2['name']}")
        print(f"  获胜者：{ending2['winner']}")
        print(f"  描述：{ending2['description'][:50]}...")
        
        game_state2.ending_triggered = True
        game_state2.ending_data = ending2
        saved = ending_storage.save_ending(ending2, 2, game_state2)
        print(f"  保存状态：{'成功' if saved else '失败'}")
    else:
        print("✗ 未触发结局")
    
    print("\n3. 测试结局三：神谕降临 (Kimi)")
    print("-" * 60)
    
    game_state3 = GameState()
    game_state3.current_year = 2054
    game_state3.current_month = 3
    
    kimi3 = Nation(
        id="nation_c",
        name="Kimi·神谕",
        ai_type=AIType.KIMI,
        resources=ResourceType(food=50000, energy=200, parts=200),
        attributes=Attributes(happiness=15, cohesion=20, military=18, prestige=210, development_speed=10),
        tech_tree=TechTree(),
        population=15000,
        territory=150,
        livability_coefficient=0.6,
        color="#9C27B0"
    )
    
    deepseek3 = Nation(
        id="nation_a",
        name="DeepSeek·仁心",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=8000, energy=40, parts=40),
        attributes=Attributes(happiness=5, cohesion=7, military=10, prestige=100, development_speed=10),
        tech_tree=TechTree(),
        population=7000,
        territory=70,
        livability_coefficient=0.8,
        color="#4CAF50"
    )
    
    aliyun3 = Nation(
        id="nation_b",
        name="阿里云百炼·铁腕",
        ai_type=AIType.ALIYUN,
        resources=ResourceType(food=8000, energy=40, parts=40),
        attributes=Attributes(happiness=4, cohesion=6, military=10, prestige=100, development_speed=10),
        tech_tree=TechTree(),
        population=7000,
        territory=70,
        livability_coefficient=0.5,
        color="#F44336"
    )
    
    game_state3.nations = {
        "nation_a": deepseek3,
        "nation_b": aliyun3,
        "nation_c": kimi3
    }
    
    game_state3.diplomatic_relations = [
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_b", hatred=40),
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_c", hatred=50),
        DiplomaticRelation(nation_a="nation_b", nation_b="nation_c", hatred=50)
    ]
    
    ending3 = ending_manager.check_endings(game_state3)
    if ending3:
        print(f"✓ 触发结局：{ending3['name']}")
        print(f"  获胜者：{ending3['winner']}")
        print(f"  描述：{ending3['description'][:50]}...")
        
        game_state3.ending_triggered = True
        game_state3.ending_data = ending3
        saved = ending_storage.save_ending(ending3, 3, game_state3)
        print(f"  保存状态：{'成功' if saved else '失败'}")
    else:
        print("✗ 未触发结局")
    
    print("\n4. 测试结局四：相安无事")
    print("-" * 60)
    
    game_state4 = GameState()
    game_state4.current_year = 2058
    game_state4.current_month = 1
    
    deepseek4 = Nation(
        id="nation_a",
        name="DeepSeek·仁心",
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=20000, energy=100, parts=100),
        attributes=Attributes(happiness=12, cohesion=12, military=12, prestige=110, development_speed=10),
        tech_tree=TechTree(),
        population=10000,
        territory=100,
        livability_coefficient=0.8,
        color="#4CAF50"
    )
    
    aliyun4 = Nation(
        id="nation_b",
        name="阿里云百炼·铁腕",
        ai_type=AIType.ALIYUN,
        resources=ResourceType(food=20000, energy=100, parts=100),
        attributes=Attributes(happiness=10, cohesion=10, military=12, prestige=100, development_speed=11),
        tech_tree=TechTree(),
        population=10000,
        territory=100,
        livability_coefficient=0.5,
        color="#F44336"
    )
    
    kimi4 = Nation(
        id="nation_c",
        name="Kimi·神谕",
        ai_type=AIType.KIMI,
        resources=ResourceType(food=20000, energy=100, parts=100),
        attributes=Attributes(happiness=11, cohesion=11, military=11, prestige=100, development_speed=9),
        tech_tree=TechTree(),
        population=10000,
        territory=100,
        livability_coefficient=0.6,
        color="#9C27B0"
    )
    
    game_state4.nations = {
        "nation_a": deepseek4,
        "nation_b": aliyun4,
        "nation_c": kimi4
    }
    
    game_state4.diplomatic_relations = [
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_b", hatred=40),
        DiplomaticRelation(nation_a="nation_a", nation_b="nation_c", hatred=40),
        DiplomaticRelation(nation_a="nation_b", nation_b="nation_c", hatred=40)
    ]
    
    ending4 = ending_manager.check_endings(game_state4)
    if ending4:
        print(f"✓ 触发结局：{ending4['name']}")
        print(f"  获胜者：{ending4['winner']}")
        print(f"  描述：{ending4['description'][:50]}...")
        
        game_state4.ending_triggered = True
        game_state4.ending_data = ending4
        saved = ending_storage.save_ending(ending4, 4, game_state4)
        print(f"  保存状态：{'成功' if saved else '失败'}")
    else:
        print("✗ 未触发结局")
    
    print("\n5. 查看所有保存的结局")
    print("-" * 60)
    all_endings = ending_storage.get_all_endings()
    print(f"总共保存了 {len(all_endings)} 个结局：")
    for i, ending in enumerate(all_endings):
        print(f"  {i+1}. {ending['结局名称']} - 序号：{ending['序号']}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_ending_system()