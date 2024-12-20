from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Vector3D:
    x: float
    y: float
    z: float

@dataclass
class Food:
    x: float
    y: float
    z: float
    points: int

@dataclass
class SpecialFood:
    x: float
    y: float
    z: float

@dataclass
class Snake:
    id: str
    direction: Vector3D
    oldDirection: Vector3D
    geometry: List[Vector3D]  # First element is head
    deathCount: int
    status: str  # 'dead' or 'alive'
    reviveRemainMs: int

@dataclass
class EnemySnake:
    geometry: List[Vector3D]  # First element is head
    status: str  # 'dead' or 'alive'
    kills: int

@dataclass
class GameState:
    name: str  # team name
    points: int
    mapSize: Vector3D
    fences: List[Vector3D]  # obstacle coordinates
    snakes: List[Snake]  # player's snakes
    enemies: List[EnemySnake]
    food: List[Food]  # regular food (mandarins)
    specialFood: List[SpecialFood]  # special food coordinates
    turn: int  # current turn number
    tickRemainMs: int  # time remaining for current turn
    reviveTimeoutSec: int  # constant time for snake revival
    errors: List[str]

@dataclass
class GameInfo:
    gameName: str
    now: str
    turn: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            gameName=data['gameName'],
            now=data['now'],
            turn=data['turn']
        )
