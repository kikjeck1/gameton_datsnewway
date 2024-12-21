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
        print("here")
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
        # Check if we need to get/update round name
        print(self.round_name)
        if not self.round_name:
            self.round_name = self._get_active_round()
            if self.round_name:
                self.logger.set_round(self.round_name)
        print(self.round_name)

        api = "/play/snake3d/player/move"
        url = f"{self.base_url}{api}"
        response = requests.post(url, headers=self.headers, json=move_data)
        print(response.status_code)
        response_data = response.json()
        # print(response_data)
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
        # results = self.read_turn_json(25)
        # game_state = parse_game_state(results)
        # print(print(get_next_state_from_game_state(game_state)))

        move = {"snakes": []}
        i = 0
        while True:
            print(i)
            result = self.make_move(move_data=move)
            for snake in result.snakes:
                print(snake.status)
                print(snake.geometry)
                print()
            move = get_next_state_from_game_state(result)
            print(move)
            time.sleep(0.5)

            # snakes = [get_next_state(snake) for snake in result.snakes]
            # move = {'snakes': snakes}
            # for snake in result.snakes:
            #     print(snake.status)
            #     print(snake.geometry)
            #     print()


if __name__ == "__main__":
    client = GameClient("https://games-test.datsteam.dev")
    client.run_client()
