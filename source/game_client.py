from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import requests
import json
from source.data_objects import Vector3D, Snake, EnemySnake, Food, SpecialFood, GameState
from source.logger import GameLogger
import time
# from source.mover import get_next
from source.mover import get_next_state_from_game_state

token = '5bcfb855-b4bc-4f27-a1ed-acee9e238b79'

class GameClient:
    def __init__(self, base_url: str = 'https://games-test.datsteam.dev'):
        self.base_url = base_url
        self.headers = {
            'X-Auth-Token': token,
            'Content-Type': 'application/json'
        }
        self.logger = GameLogger()
        self.round_name = None
        
    def _parse_game_state(self, data: dict) -> GameState:
        """Parse raw JSON response into GameState object"""
        return GameState(
            name=data.get('name', ''),
            points=data.get('points', 0),
            mapSize=Vector3D(*data['mapSize']),
            fences=[Vector3D(*fence) for fence in data.get('fences', [])],
            snakes=[Snake(
                id=s['id'],
                direction=Vector3D(*s['direction']),
                oldDirection=Vector3D(*s['oldDirection']),
                geometry=[Vector3D(*pos) for pos in s['geometry']],
                deathCount=s['deathCount'],
                status=s['status'],
                reviveRemainMs=s['reviveRemainMs']
            ) for s in data.get('snakes', [])],
            enemies=[EnemySnake(
                geometry=[Vector3D(*pos) for pos in e['geometry']],
                status=e['status'],
                kills=e.get('kills', 0)
            ) for e in data.get('enemies', [])],
            food=[Food(x=f['c'][0], y=f['c'][1], z=f['c'][2], points=f['points']) 
                  for f in data.get('food', [])],  #TODO: add special food
            specialFood=[ *[SpecialFood(x=pos[0], y=pos[1], z=pos[2])  # assuming golden food is worth 10 points
                  for pos in data.get('specialFood', {}).get('golden', [])],
                *[SpecialFood(x=pos[0], y=pos[1], z=pos[2])   # assuming suspicious food is worth 5 points
                  for pos in data.get('specialFood', {}).get('suspicious', [])]
            ],
            turn=data.get('turn', 0),
            tickRemainMs=data.get('tickRemainMs', 0),
            reviveTimeoutSec=data.get('reviveTimeoutSec', 0),
            errors=data.get('errors', [])
        )
    
    def get_game_rounds(self) -> dict:
        """Get information about game rounds"""
        api = '/rounds/snake3d'
        url = f"{self.base_url}{api}"
        print("here")
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        return response.json()
    
    def _get_active_round(self) -> Optional[str]:
        """Get the name of the currently active round"""
        rounds_info = self.get_game_rounds()
        print(rounds_info)
        active_rounds = [r for r in rounds_info['rounds'] if r['status'] == 'active']
        return active_rounds[0]['name'] if active_rounds else None
    
    def make_move(self, move_data: dict) -> GameState:
        """Make a move and log the results"""
        # Check if we need to get/update round name
        print(self.round_name)
        if not self.round_name:
            self.round_name = self._get_active_round()
            if self.round_name:
                self.logger.set_round(self.round_name)
        print(self.round_name)

        api = '/play/snake3d/player/move'
        url = f"{self.base_url}{api}"
        response = requests.post(url, headers=self.headers, json=move_data)
        print(response.status_code)
        response_data = response.json()
        # print(response_data)
        game_state = self._parse_game_state(response_data)
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
        log_path = Path(f"/Users/eaveselkov/shad/DatsNewWay/gameton_datsnewway/logs/{round_name}/turn_{turn_number}/response.json")
        
        try:
            with open(log_path, 'r') as f:
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
        # game_state = self._parse_game_state(results)
        # print(print(get_next_state_from_game_state(game_state)))

        move = {'snakes': []}
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
    client = GameClient('https://games-test.datsteam.dev')
    client.run_client()
