import logging
import json
from datetime import datetime
import os
from typing import Dict, Any
from pathlib import Path



class GameLogger:
    def __init__(self, base_dir: str = "logs"):
        self.base_dir = Path(base_dir)
        self.current_round_name: str = None
        self.session_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_logging()

    def setup_logging(self):
        # Создаем директории для логов если их нет
        self.session_dir = self.base_dir / self.session_start_time
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Настраиваем базовое логирование
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.session_dir / 'game.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def set_round(self, round_name: str):
        """Set the current round name and create its directory"""
        self.current_round_name = round_name
        round_dir = self.base_dir / round_name
        round_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Setting round to: {round_name}")
        return round_dir

    def log_request(self, move_number: int, request_data: Dict[str, Any]):
        """Логирование исходящего запроса"""
        if not self.current_round_name:
            self.logger.warning("No round set for logging request")
            return
            
        round_dir = self.base_dir / self.current_round_name
        file_path = round_dir / f"move_{move_number}_request.json"
        
        self.logger.info(f"Move {move_number} request logged")
        self._save_json(file_path, request_data)

    def log_response(self, move_number: int, response_data: Dict[str, Any]):
        """Логирование входящего ответа"""
        if not self.current_round_name:
            self.logger.warning("No round set for logging response")
            return
            
        round_dir = self.base_dir / self.current_round_name
        file_path = round_dir / f"move_{move_number}_response.json"
        
        self.logger.info(f"Move {move_number} response logged")
        self._save_json(file_path, response_data)

    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Сохранение данных в JSON файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
