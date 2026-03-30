import json
import os
from datetime import datetime
from typing import Dict, Optional


class EndingStorage:
    def __init__(self, result_file_path: str = "result"):
        self.result_file_path = result_file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.result_file_path):
            with open(self.result_file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def save_ending(self, ending_data: Dict, simulation_count: int, game_state) -> bool:
        try:
            ending_record = {
                "序号": simulation_count,
                "结局类型": ending_data.get("type", ""),
                "结局名称": ending_data.get("name", ""),
                "获胜者": ending_data.get("winner", ""),
                "达成时间": f"{game_state.current_year}年{game_state.current_month}月",
                "总月数": (game_state.current_year - 2048) * 12 + game_state.current_month,
                "结局描述": ending_data.get("description", ""),
                "达成条件": ending_data.get("conditions", {}),
                "各国最终状态": self._get_nations_summary(game_state),
                "保存时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            existing_data = self._load_existing_data()
            existing_data.append(ending_record)
            
            with open(self.result_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存结局失败: {e}")
            return False
    
    def _load_existing_data(self) -> list:
        try:
            with open(self.result_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载现有数据失败: {e}")
            return []
    
    def _get_nations_summary(self, game_state) -> Dict:
        summary = {}
        for nation_id, nation in game_state.nations.items():
            summary[nation_id] = {
                "名称": nation.name,
                "人口": nation.population,
                "领土": nation.territory,
                "幸福": nation.attributes.happiness,
                "凝聚力": nation.attributes.cohesion,
                "武力": nation.attributes.military,
                "威望": nation.attributes.prestige,
                "食物": nation.resources.food,
                "能源": nation.resources.energy,
                "经济": nation.resources.economy
            }
        return summary
    
    def get_all_endings(self) -> list:
        return self._load_existing_data()
    
    def get_ending_by_index(self, index: int) -> Optional[Dict]:
        data = self._load_existing_data()
        if 0 <= index < len(data):
            return data[index]
        return None