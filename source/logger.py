import json
from pathlib import Path
from typing import Dict, Any


class GameLogger:
    def __init__(self, base_dir: str = "logs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.game_file = None

    def set_round(self, round_name: str):
        """Setup game log file"""
        self.game_file = self.base_dir / f"{round_name}.jsonl"

    def log_turn(
        self,
        turn_number: int,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
    ):
        """Log request and response data for a specific turn"""
        if not self.game_file:
            return

        # Save request and response as single line JSON entries
        with open(self.game_file, "a", encoding="utf-8") as f:
            # f.write(json.dumps({"turn": turn_number, "request": request_data}) + "\n")
            f.write(json.dumps(response_data) + "\n")
