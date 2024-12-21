from source.data_objects import Vector3D, GameState
from typing import List, Tuple, Set

import heapq


def manhattan_distance(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def find_nearest_food(
    head: Tuple[int, int, int], food_list: List[Tuple[int, int, int, int]], top_k=10
) -> List[Tuple[int, int, int]]:
    """Find top 3 nearest food items using Manhattan distance"""
    if not food_list:
        return []
    distances = [
        (f[-1] / (manhattan_distance(head, f[:3]) ** 2), f)  # See Kostyl ** 2
        for f in food_list
        if f[-1] > 0
    ]
    distances.sort(key=lambda x: -x[0])  # Sort by  points / distance
    return [f[1][:3] for f in distances[:top_k]]  # Return top k foods


def is_valid_position(
    pos: Tuple[int, int, int],
    map_size: Vector3D,
    obstacles: Set[Tuple[int, int, int]],
    snake_body: Set[Tuple[int, int, int]],
) -> bool:
    """Check if position is valid (within bounds and not in obstacles)"""
    x, y, z = pos
    return (
        0 <= x < map_size.x
        and 0 <= y < map_size.y
        and 0 <= z < map_size.z
        and pos not in obstacles
        and pos not in snake_body
    )


def a_star_search(
    start: Tuple[int, int, int],
    goal: Tuple[int, int, int],
    obstacles: Set[Tuple[int, int, int]],
    snake_body: Set[Tuple[int, int, int]],
    map_size: Vector3D,
) -> List[Tuple[int, int, int]]:
    """
    A* implementation with map boundaries and movement rules
    """

    def heuristic(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
        """Manhattan distance between two points"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def get_neighbors(node: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get valid neighbors respecting map boundaries and obstacles"""
        directions = [
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        ]
        neighbors = []
        for dx, dy, dz in directions:
            new_pos = (node[0] + dx, node[1] + dy, node[2] + dz)
            if is_valid_position(new_pos, map_size, obstacles, snake_body):
                neighbors.append(new_pos)
        return neighbors

    # Initialize A* data structures
    open_set = []
    heapq.heappush(open_set, (0, start))
    closed_set = set()
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    came_from = {}

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        closed_set.add(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f = tentative_g_score + heuristic(neighbor, goal)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))

    return []


def get_next_state_from_game_state(game_state: GameState) -> dict:
    """Calculate next moves for all snakes"""
    snake_moves = {"snakes": []}

    # Collect obstacles
    obstacles = {(fence.x, fence.y, fence.z) for fence in game_state.fences}
    
    for snake in game_state.snakes:
        if snake.status == "alive":
            # Add all segments except the last one
            obstacles.update(
                (segment.x, segment.y, segment.z)
                for segment in snake.geometry[:-1]  # TODO: add more complex logic
            )
            
    for snake in game_state.enemies:
        if snake.status == "alive":
            
            obstacles.update(
                (segment.x, segment.y, segment.z)
                for segment in snake.geometry[:-1]  # TODO: add more complex logic
            )
            
            head = snake.geometry[0]
            possible_head_positions = [
                (head.x + dx, head.y + dy, head.z + dz)
                for dx, dy, dz in [
                    (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)
                ]
            ]
            obstacles.update(possible_head_positions)

    # Process each snake
    for snake in game_state.snakes:
        if snake.status == "dead":
            snake_moves["snakes"].append({"id": snake.id, "direction": [0, 0, 0]})
            continue

        # Get snake head and body
        head = (snake.geometry[0].x, snake.geometry[0].y, snake.geometry[0].z)
        snake_body = {
            (segment.x, segment.y, segment.z) for segment in snake.geometry[1:]
        }

        # Collect and find nearest food
        all_food = [(food.x, food.y, food.z, food.points) for food in game_state.food]
        nearest_food = find_nearest_food(head, all_food, top_k=5)

        # Find best path to nearest food
        best_path = None
        for food_pos in nearest_food:
            path = a_star_search(
                head, food_pos, obstacles, snake_body, game_state.mapSize
            )
            if path and (best_path is None or len(path) < len(best_path)):
                best_path = path

        # Calculate direction
        direction = [0, 0, 0]  # Default direction if no valid move found

        if best_path and len(best_path) > 1:
            next_pos = best_path[1]
            direction = [
                next_pos[0] - head[0],
                next_pos[1] - head[1],
                next_pos[2] - head[2],
            ]
        else:
            # Try to find any safe direction
            for test_dir in [
                (1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1),
            ]:
                test_pos = (
                    head[0] + test_dir[0],
                    head[1] + test_dir[1],
                    head[2] + test_dir[2],
                )
                if is_valid_position(
                    test_pos, game_state.mapSize, obstacles, snake_body
                ):
                    direction = list(test_dir)
                    break

        snake_moves["snakes"].append({"id": snake.id, "direction": direction})

    return snake_moves
