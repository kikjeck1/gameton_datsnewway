import json
from pathlib import Path
from typing import Dict, Any

class GameLogger:
    def __init__(self, base_dir: str = "logs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.round_dir = None
        
    def set_round(self, round_name: str):
        """Setup logging directory for a specific round"""
        self.round_dir = self.base_dir / round_name
        self.round_dir.mkdir(exist_ok=True)
        
    def log_turn(self, turn_number: int, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """Log request and response data for a specific turn"""
        if not self.round_dir:
            return
            
        turn_dir = self.round_dir / f'turn_{turn_number}'
        turn_dir.mkdir(exist_ok=True)
        
        # Save request and response
        with open(turn_dir / 'request.json', 'w', encoding='utf-8') as f:
            json.dump(request_data, f, indent=2)
            
        with open(turn_dir / 'response.json', 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2)
