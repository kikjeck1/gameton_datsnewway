from source.data_objects import Vector2D, Transport, Enemy, Anomaly, Bounty, GameState
import random


class GameError(Exception):
    def __init__(self, error_code: int, error_message: str):
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f"Game Error {error_code}: {error_message}")

def generate_sample_game_state(move_number: int) -> dict:
    """Generate sample game state with variations based on move number"""
    base_state = {
        "name": "test_game",
        "points": 100 + (move_number * 50),  # Points increase with each move
        "mapSize": {"x": 1000.0, "y": 1000.0},
        "transportRadius": 10.0,
        "maxSpeed": 100.0,
        "maxAccel": 10.0,
        "attackRange": 50.0,
        "attackDamage": 25,
        "attackExplosionRadius": 20.0,
        "attackCooldownMs": 1000,
        "shieldTimeMs": 5000,
        "shieldCooldownMs": 10000,
        "reviveTimeoutSec": 30,
        "transports": [{
            "id": "transport-1",
            "x": 100.0 + (move_number * 50),  # Transport moves with each move
            "y": 100.0 + (move_number * 30),
            "health": 100 - (move_number * 10),  # Health decreases with each move
            "status": "active",
            "velocity": {"x": 5.0, "y": 3.0},
            "anomalyAcceleration": {"x": 0.0, "y": 0.0},
            "selfAcceleration": {"x": 2.0, "y": 1.0},
            "attackCooldownMs": 0,
            "shieldCooldownMs": 0,
            "shieldLeftMs": 0,
            "deathCount": 0
        }],
        "enemies": [{
            "x": 500.0 - (move_number * 20),  # Enemy moves opposite to transport
            "y": 500.0 - (move_number * 15),
            "health": 80,
            "status": "active",
            "velocity": {"x": -3.0, "y": -2.0},
            "shieldLeftMs": 0,
            "killBounty": 100
        }],
        "wantedList": [],
        "anomalies": [{
            "id": "anomaly-1",
            "x": 300.0,
            "y": 300.0,
            "radius": 50.0,
            "effectiveRadius": 100.0,
            "strength": 5.0,
            "velocity": {"x": 0.0, "y": 0.0}
        }],
        "bounties": [{
            "x": 800.0,
            "y": 800.0,
            "radius": 30.0,
            "points": 200
        }]
    }
    return base_state

def parse_game_state(data: dict) -> GameState:
    # Преобразование JSON-ответа в объект GameState
    return GameState(
        name=data['name'],
        points=data['points'],
        mapSize=Vector2D(**data['mapSize']),
        transportRadius=data['transportRadius'],
        maxSpeed=data['maxSpeed'],
        maxAccel=data['maxAccel'],
        attackRange=data['attackRange'],
        attackDamage=data['attackDamage'],
        attackExplosionRadius=data['attackExplosionRadius'],
        attackCooldownMs=data['attackCooldownMs'],
        shieldTimeMs=data['shieldTimeMs'],
        shieldCooldownMs=data['shieldCooldownMs'],
        reviveTimeoutSec=data['reviveTimeoutSec'],
        transports=[Transport(**t) for t in data['transports']],
        enemies=[Enemy(**e) for e in data['enemies']],
        wantedList=[Enemy(**w) for w in data['wantedList']],
        anomalies=[Anomaly(**a) for a in data['anomalies']],
        bounties=[Bounty(**b) for b in data['bounties']]
    )
