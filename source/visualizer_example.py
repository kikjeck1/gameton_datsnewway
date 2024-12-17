from source.visualizer import Visualizer
from source.game_client import GameClient
from source.data_objects import Vector2D
from pathlib import Path

def replay_example():
    """Example of replaying a recorded round"""
    visualizer = Visualizer()
    logs_path = Path("logs/test_round")
    visualizer.replay_from_logs(logs_path)

def realtime_example():
    """Example of real-time visualization"""
    client = GameClient("http://localhost:5000")
    visualizer = Visualizer()
    
    running = True
    while running:
        game_state = client.send_move(
            transport_id="transport-1",
            acceleration=Vector2D(0.0, 0.0)
        )
        running = visualizer.run_realtime(game_state)

if __name__ == "__main__":
    # Choose which example to run
    replay_example()
    # realtime_example()