from fastapi import APIRouter, HTTPException
from typing import Dict, List
from models.entities import GameState, Nation, AIType, AI_CONFIGS, ResourceType, Attributes, TechTree
from models.schemas.schemas import GameStateSchema, NationSchema, PlayerActionSchema
from game_engine.game_engine import GameEngine
from ai_agents.agent_manager import AIAgentManager
import os


router = APIRouter(prefix="/game", tags=["game"])

game_engine = GameEngine()
ai_agent_manager = None


def initialize_game_state():
    global ai_agent_manager
    
    api_keys = {
        "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
        "aliyun": os.getenv("ALIYUN_API_KEY", ""),
        "kimi": os.getenv("KIMI_API_KEY", "")
    }
    
    ai_agent_manager = AIAgentManager(api_keys)
    
    game_state = GameState()
    
    deepseek_config = AI_CONFIGS["deepseek"]
    aliyun_config = AI_CONFIGS["aliyun"]
    kimi_config = AI_CONFIGS["kimi"]
    
    nation_a = Nation(
        id="nation_a",
        name=deepseek_config.name,
        ai_type=AIType.DEEPSEEK,
        resources=ResourceType(food=20000, energy=20000, economy=20000),
        attributes=Attributes(**deepseek_config.initial_attributes),
        tech_tree=TechTree(),
        color="#4CAF50"
    )
    
    nation_b = Nation(
        id="nation_b",
        name=aliyun_config.name,
        ai_type=AIType.ALIYUN,
        resources=ResourceType(food=20000, energy=20000, economy=20000),
        attributes=Attributes(**aliyun_config.initial_attributes),
        tech_tree=TechTree(),
        color="#F44336"
    )
    
    nation_c = Nation(
        id="nation_c",
        name=kimi_config.name,
        ai_type=AIType.KIMI,
        resources=ResourceType(food=20000, energy=20000, economy=20000),
        attributes=Attributes(**kimi_config.initial_attributes),
        tech_tree=TechTree(),
        livability_coefficient=0.6,
        color="#9C27B0"
    )
    
    game_state.nations = {
        "nation_a": nation_a,
        "nation_b": nation_b,
        "nation_c": nation_c
    }
    
    game_engine.initialize_game(game_state)
    ai_agent_manager.initialize_agents(game_state)
    
    return game_state


current_game_state = initialize_game_state()


@router.get("/state", response_model=GameStateSchema)
async def get_game_state():
    return GameStateSchema(
        current_month=current_game_state.current_month,
        current_year=current_game_state.current_year,
        nations={
            nation_id: NationSchema(
                id=nation.id,
                name=nation.name,
                ai_type=nation.ai_type.value,
                resources={
                    "food": nation.resources.food,
                    "energy": nation.resources.energy,
                    "economy": nation.resources.economy
                },
                attributes={
                    "happiness": nation.attributes.happiness,
                    "cohesion": nation.attributes.cohesion,
                    "military": nation.attributes.military,
                    "prestige": nation.attributes.prestige,
                    "development_speed": nation.attributes.development_speed
                },
                tech_tree={
                    "military_level": nation.tech_tree.military_level,
                    "social_level": nation.tech_tree.social_level,
                    "exploration_level": nation.tech_tree.exploration_level
                },
                population=nation.population,
                territory=nation.territory,
                color=nation.color
            )
            for nation_id, nation in current_game_state.nations.items()
        },
        diplomatic_relations=[
            {
                "nation_a": relation.nation_a,
                "nation_b": relation.nation_b,
                "hatred": relation.hatred,
                "alliance": relation.alliance,
                "trade_agreement": relation.trade_agreement
            }
            for relation in current_game_state.diplomatic_relations
        ],
        active_wars=[
            {
                "attacker": war.attacker,
                "defender": war.defender,
                "start_month": war.start_month,
                "is_active": war.is_active
            }
            for war in current_game_state.active_wars
        ],
        event_history=current_game_state.event_history
    )


@router.post("/advance")
async def advance_month():
    global current_game_state
    try:
        ai_decisions = ai_agent_manager.process_all_decisions(current_game_state)
        results = game_engine.process_month(current_game_state)
        results["ai_decisions"] = ai_decisions
        
        ending_result = game_engine.handle_ending_triggered(current_game_state)
        results["ending"] = ending_result
        
        if ending_result.get("ending_triggered"):
            current_game_state = initialize_game_state()
            results["game_reset"] = True
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action")
async def handle_player_action(action: PlayerActionSchema):
    try:
        result = game_engine.handle_player_action(current_game_state, action.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/{nation_id}")
async def send_chat_message(nation_id: str, message: Dict):
    try:
        content = message.get("content", "")
        sender = message.get("sender", "player")
        
        response = ai_agent_manager.process_chat_message(nation_id, content, sender)
        
        return {
            "nation_id": nation_id,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{nation_id}")
async def get_chat_history(nation_id: str):
    try:
        history = ai_agent_manager.get_chat_history(nation_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_game():
    global current_game_state
    current_game_state = initialize_game_state()
    return {"message": "游戏已重置"}


@router.get("/endings")
async def get_all_endings():
    try:
        endings = game_engine.ending_storage.get_all_endings()
        return {"endings": endings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/endings/{index}")
async def get_ending_by_index(index: int):
    try:
        ending = game_engine.ending_storage.get_ending_by_index(index)
        if ending:
            return {"ending": ending}
        else:
            raise HTTPException(status_code=404, detail="结局不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
