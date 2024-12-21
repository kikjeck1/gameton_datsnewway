from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import requests
import json
from source.data_objects import GameState

from source.logger import GameLogger
import time

from source.utils import parse_game_state

# from source.mover import get_next
from source.mover import get_next_state_from_game_state

token = "5bcfb855-b4bc-4f27-a1ed-acee9e238b79"


def measure_execution_time(func_name):
    """Decorator to measure and print execution time"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            print(f"{func_name} execution time: {execution_time:.2f}ms")
            return result, execution_time

        return wrapper

    return decorator


class GameClient:
    def __init__(self, base_url: str = "http://games-test.datsteam.dev"):
        self.base_url = base_url
        self.headers = {
            "X-Auth-Token": token,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
        }
        self.logger = GameLogger()
        self.round_name = None

    def get_game_rounds(self) -> dict:
        """Get information about game rounds"""
        api = "/rounds/snake3d"
        url = f"{self.base_url}{api}"
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        return response.json()

    def _get_active_round(self) -> Optional[str]:
        """Get the name of the currently active round"""
        rounds_info = self.get_game_rounds()
        print(rounds_info)
        active_rounds = [r for r in rounds_info["rounds"] if r["status"] == "active"]
        return active_rounds[0]["name"] if active_rounds else None

    def make_move(self, move_data: dict) -> GameState:
        """Make a move and log the results"""
        if not self.round_name:
            self.round_name = self._get_active_round()
            if self.round_name:
                self.logger.set_round(self.round_name)

        # Make API request
        api = "/play/snake3d/player/move"
        url = f"{self.base_url}{api}"
        response = requests.post(url, headers=self.headers, json=move_data)
        response_data = response.json()

        game_state = parse_game_state(response_data)

        if self.round_name:
            self.logger.log_turn(game_state.turn, move_data, response_data)

        return game_state

    def read_turn_json(self, turn_number: int) -> dict:
        """Read JSON response data from a specific turn's log file

        Args:
            turn_number: The turn number to read data from

        Returns:
            dict: The JSON data from the response file
        """
        round_name = 2
        log_path = Path(
            f"/Users/eaveselkov/shad/DatsNewWay/gameton_datsnewway/logs/{round_name}/turn_{turn_number}/response.json"
        )

        try:
            with open(log_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"No log file found for turn {turn_number}")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from turn {turn_number}")
            return {}

    def run_client(self):
        """Main client loop"""
        move = {"snakes": []}

        # Apply decorators
        make_move_timed = measure_execution_time("make_move")(self.make_move)
        get_next_state_timed = measure_execution_time("get_next_state")(
            get_next_state_from_game_state
        )

        while True:
            result, move_time = make_move_timed(move_data=move)
            move, state_time = get_next_state_timed(result)

            total_execution_time = move_time + state_time
            sleep_time = max(
                0, (result.tickRemainMs - total_execution_time) / 1000 + 0.6
            )

            # Выводим дополнительную информацию о змеях
            print("Turn:", result.turn)
            print("Tick remain:", result.tickRemainMs)
            print("Snakes:", result.snakes)
            for snake in result.snakes:
                print(snake.status)
            print()

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                print("Warning: Processing took longer than tick time!")


if __name__ == "__main__":
    client = GameClient("https://games-test.datsteam.dev")
    client.run_client()
