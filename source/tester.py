import json
from source.data_objects import GameState, Vector3D, Snake, Food, Fence
from source.mover import get_next_state_from_game_state


def parse_json_to_game_state(json_data):
    """Convert JSON data to GameState object"""
    data = json.loads(json_data)

    # Parse map size
    map_size = Vector3D(
        data["params"]["map_size"][0],
        data["params"]["map_size"][1],
        data["params"]["map_size"][2],
    )

    # Parse snakes
    snakes = []
    for snake_data in data["snakes"]:
        geometry = [Vector3D(p[0], p[1], p[2]) for p in snake_data["coords"]]
        direction = Vector3D(
            snake_data["direction"][0],
            snake_data["direction"][1],
            snake_data["direction"][2],
        )
        snake = Snake(
            id=snake_data["id"],
            geometry=geometry,
            direction=direction,
            status=snake_data["status"],
        )
        snakes.append(snake)

    # Parse food
    food = []
    for food_data in data["food"]:
        food_item = Food(
            x=food_data["c"][0],
            y=food_data["c"][1],
            z=food_data["c"][2],
            points=food_data["points"],
        )
        food.append(food_item)

    # Parse fences
    fences = []
    for fence_data in data.get("fences", []):
        fence = Fence(x=fence_data[0], y=fence_data[1], z=fence_data[2])
        fences.append(fence)

    # Create GameState
    game_state = GameState(
        mapSize=map_size,
        snakes=snakes[:1],  # First snake is ours
        enemies=snakes[1:],  # Rest are enemies
        food=food,
        fences=fences,
    )

    return game_state


def test_move(json_data):
    """Test the algorithm with JSON input"""
    # Parse JSON into GameState
    game_state = parse_json_to_game_state(json_data)

    # Get next move
    result = get_next_state_from_game_state(game_state)

    return result


if __name__ == "__main__":
    # Example usage
    with open("game_state.json", "r") as f:
        json_data = f.read()

    result = test_move(json_data)
    print(json.dumps(result, indent=2))
