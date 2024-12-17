from pathlib import Path
import json
from source.utils import generate_sample_game_state

def generate_sample_moves():
    # Create test round directory
    round_dir = Path("logs/test_round")
    round_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 3 moves with slightly different data
    for move_number in range(1, 20):
        game_state = generate_sample_game_state(move_number)
        
        # Save response file
        response_file = round_dir / f"move_{move_number}_response.json"
        with open(response_file, 'w') as f:
            json.dump(game_state, f, indent=2)
        
        print(f"Generated {response_file}")

if __name__ == "__main__":
    generate_sample_moves() 