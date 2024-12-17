from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Тестовые данные
SAMPLE_GAME_RESPONSE = {
    "name": "test_game",
    "points": 100,
    "mapSize": {"x": 1000, "y": 1000},
    "transportRadius": 10,
    "maxSpeed": 50,
    "maxAccel": 5,
    "attackRange": 100,
    "attackDamage": 25,
    "attackExplosionRadius": 20,
    "attackCooldownMs": 1000,
    "shieldTimeMs": 2000,
    "shieldCooldownMs": 5000,
    "reviveTimeoutSec": 10,
    "transports": [
        {
            "id": "transport-1",
            "position": {"x": 100, "y": 100},
            "velocity": {"x": 0, "y": 0},
            "health": 100,
            "shield": False
        }
    ],
    "enemies": [
        {
            "id": "enemy-1",
            "position": {"x": 200, "y": 200},
            "velocity": {"x": 1, "y": 1},
            "health": 100,
            "shield": False
        }
    ],
    "wantedList": [],
    "anomalies": [
        {
            "position": {"x": 300, "y": 300},
            "radius": 50
        }
    ],
    "bounties": [
        {
            "position": {"x": 400, "y": 400},
            "value": 50
        }
    ]
}

SAMPLE_ROUND_RESPONSE = {
    "gameName": "magcarp",
    "now": "2024-02-15T12:00:00Z",
    "rounds": [
        {
            "name": "round-1",
            "status": "active",
            "startAt": "2024-02-15T12:00:00Z",
            "endAt": "2024-02-15T13:00:00Z",
            "duration": 3600,
            "repeat": 1
        }
    ]
}

@app.route('/rounds/magcarp', methods=['GET'])
def get_round():
    print("GET /rounds/magcarp")
    print("Response:", SAMPLE_ROUND_RESPONSE)
    return jsonify(SAMPLE_ROUND_RESPONSE)

@app.route('/play/magcarp/player/move', methods=['POST'])
def make_move():
    print("\nPOST /play/magcarp/player/move")
    print("Request data:", request.json)
    
    # Имитация проверки данных
    if 'transports' not in request.json:
        return jsonify({
            "errCode": 1001,
            "error": "Invalid request format"
        }), 400

    transport = request.json['transports'][0]
    if 'id' not in transport:
        return jsonify({
            "errCode": 1002,
            "error": "Transport ID is required"
        }), 400

    # Имитация задержки сервера
    time.sleep(0.1)
    
    print("Response:", SAMPLE_GAME_RESPONSE)
    return jsonify(SAMPLE_GAME_RESPONSE)

if __name__ == '__main__':
    app.run(port=5000)