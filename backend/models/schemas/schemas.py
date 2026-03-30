from pydantic import BaseModel
from typing import Dict, List, Optional


class NationSchema(BaseModel):
    id: str
    name: str
    ai_type: str
    resources: Dict[str, int]
    attributes: Dict[str, int]
    tech_tree: Dict[str, int]
    population: int
    territory: float
    color: str


class GameStateSchema(BaseModel):
    current_month: int
    current_year: int
    nations: Dict[str, NationSchema]
    diplomatic_relations: List[Dict]
    active_wars: List[Dict]
    event_history: List[str]


class ChatMessageSchema(BaseModel):
    sender: str
    content: str
    timestamp: str


class AIResponseSchema(BaseModel):
    nation_id: str
    message: str
    action: Optional[str] = None
    target_nation: Optional[str] = None


class PlayerActionSchema(BaseModel):
    action_type: str
    target_nation: Optional[str] = None
    parameters: Dict = {}
