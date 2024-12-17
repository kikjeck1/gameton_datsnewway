from source.game_client import GameClient
from source.data_objects import Vector2D
from source.utils import GameError
import pytest
from unittest.mock import patch, Mock
import json

def test_client():
    # Mock the requests to avoid actual HTTP calls
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        # Setup mock responses
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "gameName": "test_game",
                "now": "2024-01-01T00:00:00Z",
                "rounds": [{
                    "name": "test_round",
                    "status": "active",
                    "startAt": "2024-01-01T00:00:00Z",
                    "endAt": "2024-01-01T01:00:00Z",
                    "duration": 3600,
                    "repeat": 1
                }]
            }
        )

        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "name": "test_game",
                "points": 100,
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
                "transports": [],
                "enemies": [],
                "wantedList": [],
                "anomalies": [],
                "bounties": []
            }
        )

        client = GameClient("http://localhost:5000")
        
        # Test round check
        print("\nChecking rounds...")
        round_info = client.check_round()
        assert round_info.gameName == "test_game"
        print(f"Round info received: {round_info}")

        # Test move
        print("\nMaking move...")
        game_state = client.send_move(
            transport_id="transport-1",
            acceleration=Vector2D(1.0, 1.0),
            attack=Vector2D(2.0, 2.0),
            activate_shield=True
        )
        assert game_state.name == "test_game"
        print(f"Move completed, game state received: {game_state}")

        # Test error handling
        print("\nTesting error handling...")
        mock_post.return_value = Mock(status_code=400)
        with pytest.raises(GameError):
            game_state = client.send_move(
                transport_id="",  # Empty ID to trigger error
                acceleration=Vector2D(1.0, 1.0)
            )
            print("Error handling test passed")

if __name__ == '__main__':
    test_client()