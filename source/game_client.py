from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging
import requests
import json
from source.utils import GameError
from source.data_objects import Vector2D, Transport, Enemy, Anomaly, Bounty, GameInfo, GameState
from source.logger import GameLogger


class GameClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.logger = GameLogger()
        self.move_counter = 0
        self.current_round_info = None

    def check_round(self) -> GameInfo:
        """Получение информации о текущих раундах"""
        response = requests.get(f"{self.base_url}/rounds/magcarp")
        if response.status_code == 200:
            return GameInfo.from_dict(response.json())
        else:
            raise GameError(response.status_code, f"Failed to check round status")

    def update_round(self) -> Optional[str]:
        """Обновление информации о текущем раунде"""
        game_info = self.check_round()
        
        # Находим активный раунд
        active_rounds = [r for r in game_info.rounds if r.status == "active"]
        if not active_rounds:
            self.logger.logger.warning("No active rounds found")
            return None

        current_round = active_rounds[0]
        
        # Если раунд изменился
        if not self.current_round_info or self.current_round_info.name != current_round.name: 
            self.current_round_info = current_round
            self.move_counter = 0
            self.logger.set_round(current_round.name)
            self.logger.logger.info(f"Switched to round: {current_round.name}")
            
            # Логируем информацию о раунде
            round_info_path = self.logger.base_dir / current_round.name / "round_info.json"
            with open(round_info_path, 'w') as f:
                json.dump(vars(current_round), f, indent=2)

        return current_round.name

    def send_move(self, transport_id: str, acceleration: Vector2D, 
                  attack: Optional[Vector2D] = None, activate_shield: bool = False):
        """Отправка хода и логирование"""
        # Проверяем/обновляем информацию о раунде перед каждым ходом
        current_round = self.update_round()
        if not current_round:
            raise Exception("No active round available")

        self.move_counter += 1
        
        # Формируем данные запроса
        move_data = {
            "transports": [{
                "id": transport_id,
                "acceleration": {"x": acceleration.x, "y": acceleration.y},
                "activateShield": activate_shield
            }]
        }
        if attack:
            move_data["transports"][0]["attack"] = {"x": attack.x, "y": attack.y}

        # Логируем запрос
        self.logger.log_request(self.move_counter, move_data)

        # Отправляем запрос
        response = requests.post(
            f"{self.base_url}/play/magcarp/player/move",
            headers=self.headers,
            json=move_data
        )

        if response.status_code == 200:
            response_data = response.json()
            # Логируем ответ
            self.logger.log_response(self.move_counter, response_data)
            return self._parse_game_state(response_data)
        else:
            error_msg = f"Failed to send move"
            self.logger.logger.error(error_msg)
            raise GameError(response.status_code, error_msg)

    def _parse_game_state(self, data: dict) -> GameState:
        # Преобразование JSON-ответа в объект GameState
        return GameState(
            name=data['name'],
            points=data['points'],
            map_size=Vector2D(**data['mapSize']),
            transport_radius=data['transportRadius'],
            max_speed=data['maxSpeed'],
            max_accel=data['maxAccel'],
            attack_range=data['attackRange'],
            attack_damage=data['attackDamage'],
            attack_explosion_radius=data['attackExplosionRadius'],
            attack_cooldown_ms=data['attackCooldownMs'],
            shield_time_ms=data['shieldTimeMs'],
            shield_cooldown_ms=data['shieldCooldownMs'],
            revive_timeout_sec=data['reviveTimeoutSec'],
            transports=[Transport(**t) for t in data['transports']],
            enemies=[Enemy(**e) for e in data['enemies']],
            wanted_list=[Enemy(**w) for w in data['wantedList']],
            anomalies=[Anomaly(**a) for a in data['anomalies']],
            bounties=[Bounty(**b) for b in data['bounties']]
        )

# # Пример использования:
# if __name__ == "__main__":
#     client = GameClient("https://games.datsteam.dev")
    
#     # Пример отправки хода
#     try:
#         print(client.check_round())
#         game_state = client.send_move(
#             transport_id="00000000-0000-0000-0000-000000000000",
#             acceleration=Vector2D(1.2, 1.2),
#             attack=Vector2D(1.0, 1.0),
#             activate_shield=True
#         )
