import json
from source.mover import get_next_state_from_game_state
from source.utils import parse_game_state


def test_move(json_data):
    """Test the algorithm with JSON input"""
    game_state = parse_game_state(json_data)
    result = get_next_state_from_game_state(game_state)

    return result


if __name__ == "__main__":
    TURN = 1467
    with open(
        "/Users/eaveselkov/shad/DatsNewWay/gameton_datsnewway/logs/snake3d-day2-3.jsonl",
        "r",
    ) as f:
        if TURN is not None:
            for json_data in f.readlines():
                if json.loads(json_data)["turn"] == TURN:
                    break
        else:
            json_data = f.read()

    result = test_move(json.loads(json_data))
    print(json.dumps(result, indent=2))
