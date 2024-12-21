from source.data_objects import (
    Vector3D,
    Snake,
    EnemySnake,
    Food,
    SpecialFood,
    GameState,
)


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
        "transports": [
            {
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
                "deathCount": 0,
            }
        ],
        "enemies": [
            {
                "x": 500.0 - (move_number * 20),  # Enemy moves opposite to transport
                "y": 500.0 - (move_number * 15),
                "health": 80,
                "status": "active",
                "velocity": {"x": -3.0, "y": -2.0},
                "shieldLeftMs": 0,
                "killBounty": 100,
            }
        ],
        "wantedList": [],
        "anomalies": [
            {
                "id": "anomaly-1",
                "x": 300.0,
                "y": 300.0,
                "radius": 50.0,
                "effectiveRadius": 100.0,
                "strength": 5.0,
                "velocity": {"x": 0.0, "y": 0.0},
            }
        ],
        "bounties": [{"x": 800.0, "y": 800.0, "radius": 30.0, "points": 200}],
    }
    return base_state


def parse_game_state(data: dict) -> GameState:
    """Parse raw JSON response into GameState object"""
    return GameState(
        name=data.get("name", ""),
        points=data.get("points", 0),
        mapSize=Vector3D(*data["mapSize"]),
        fences=[Vector3D(*fence) for fence in data.get("fences", [])],
        snakes=[
            Snake(
                id=s["id"],
                direction=Vector3D(*s["direction"]),
                oldDirection=Vector3D(*s["oldDirection"]),
                geometry=[Vector3D(*pos) for pos in s["geometry"]],
                deathCount=s["deathCount"],
                status=s["status"],
                reviveRemainMs=s["reviveRemainMs"],
            )
            for s in data.get("snakes", [])
        ],
        enemies=[
            EnemySnake(
                geometry=[Vector3D(*pos) for pos in e["geometry"]],
                status=e["status"],
                kills=e.get("kills", 0),
            )
            for e in data.get("enemies", [])
        ],
        food=[
            Food(x=f["c"][0], y=f["c"][1], z=f["c"][2], points=f["points"])
            for f in data.get("food", [])
        ],  # TODO: add special food
        specialFood=[
            *[
                SpecialFood(
                    x=pos[0], y=pos[1], z=pos[2]
                )  # assuming golden food is worth 10 points
                for pos in data.get("specialFood", {}).get("golden", [])
            ],
            *[
                SpecialFood(
                    x=pos[0], y=pos[1], z=pos[2]
                )  # assuming suspicious food is worth 5 points
                for pos in data.get("specialFood", {}).get("suspicious", [])
            ],
        ],
        turn=data.get("turn", 0),
        tickRemainMs=data.get("tickRemainMs", 0),
        reviveTimeoutSec=data.get("reviveTimeoutSec", 0),
        errors=data.get("errors", []),
    )
