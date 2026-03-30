from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from .nation import Nation, AIType


class DiplomaticRelation(BaseModel):
    nation_a: str
    nation_b: str
    hatred: int = 40
    alliance: bool = False
    trade_agreement: bool = False


class WarState(BaseModel):
    attacker: str
    defender: str
    start_month: int
    end_month: Optional[int] = None
    attackers_allies: List[str] = []
    defenders_allies: List[str] = []
    is_active: bool = True


class GameState(BaseModel):
    current_month: int = 1
    current_year: int = 2048
    nations: Dict[str, Nation] = {}
    diplomatic_relations: List[DiplomaticRelation] = []
    active_wars: List[WarState] = []
    event_history: List[str] = []
    chat_history: Dict[str, List[Dict]] = {}
    advantage_tracker: Dict[str, Dict[str, int]] = {}
    ending_triggered: bool = False
    ending_data: Optional[Dict] = None
    simulation_count: int = 0
    
    def get_nation(self, nation_id: str) -> Optional[Nation]:
        return self.nations.get(nation_id)
    
    def get_relation(self, nation_a: str, nation_b: str) -> Optional[DiplomaticRelation]:
        for relation in self.diplomatic_relations:
            if (relation.nation_a == nation_a and relation.nation_b == nation_b) or \
               (relation.nation_a == nation_b and relation.nation_b == nation_a):
                return relation
        return None
    
    def advance_time(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
