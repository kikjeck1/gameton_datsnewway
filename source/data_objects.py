from dataclasses import dataclass
from typing import List

@dataclass
class Vector2D:
    x: float
    y: float

@dataclass
class Transport:
    id: str
    x: float
    y: float
    health: int
    status: str
    velocity: Vector2D
    anomalyAcceleration: Vector2D
    selfAcceleration: Vector2D
    attackCooldownMs: int
    shieldCooldownMs: int
    shieldLeftMs: int
    deathCount: int

@dataclass
class Enemy:
    x: float
    y: float
    health: int
    status: str
    velocity: Vector2D
    shieldLeftMs: int
    killBounty: int

@dataclass
class Anomaly:
    id: str
    x: float
    y: float
    radius: float
    effectiveRadius: float
    strength: float
    velocity: Vector2D

@dataclass
class Bounty:
    x: float
    y: float
    radius: float
    points: int

@dataclass
class GameState:
    name: str
    points: int
    mapSize: Vector2D
    transportRadius: float
    maxSpeed: float
    maxAccel: float
    attackRange: float
    attackDamage: float
    attackExplosionRadius: float
    attackCooldownMs: int
    shieldTimeMs: int
    shieldCooldownMs: int
    reviveTimeoutSec: int
    transports: List[Transport]
    enemies: List[Enemy]
    wantedList: List[Enemy]
    anomalies: List[Anomaly]
    bounties: List[Bounty]

@dataclass
class Round:
    name: str
    status: str
    startAt: str
    endAt: str
    duration: int
    repeat: int

@dataclass
class GameInfo:
    gameName: str
    now: str
    rounds: List[Round]

    @classmethod
    def from_dict(cls, data: dict):
        rounds = [Round(**round_data) for round_data in data['rounds']]
        return cls(
            gameName=data['gameName'],
            now=data['now'],
            rounds=rounds
        )
