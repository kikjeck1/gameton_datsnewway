from source.data_objects import Vector3D, GameState
from typing import List, Tuple, Set
from source.data_objects import Snake

import heapq
import random

def check_that_dead_end(pos: Tuple[int, int, int], obstacles: Set[Tuple[int, int, int]], head: Tuple[int, int, int]) -> bool:
    directions = [
        (1, 0, 0), 
        (-1, 0, 0), 
        (0, 1, 0),  
        (0, -1, 0),
        (0, 0, 1), 
        (0, 0, -1)  
    ]
    exit_count = 0
    for dx, dy, dz in directions:
        new_pos = (pos[0] + dx, pos[1] + dy, pos[2] + dz)
        if (new_pos not in obstacles) or new_pos == head:
            exit_count += 1
    return exit_count < 2
     

def manhattan_distance(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def get_offset(game_state: GameState) -> int:
    if game_state.turn <= 500:
        return 0
    else:
        return 1


def get_directions(game_state: GameState, snake: Snake) -> List[Tuple[int, int, int]]:
    head = snake.geometry[0]
    center = (
        game_state.mapSize.x // 2,
        game_state.mapSize.y // 2,
        game_state.mapSize.z // 2,
    )
    distance_to_center = manhattan_distance((head.x, head.y, head.z), center)

    if game_state.turn <= 500:
        # First 500 turns: move towards center
        center_directions = []
        if head.x < center[0]:
            center_directions.append((1, 0, 0))
        elif head.x > center[0]:
            center_directions.append((-1, 0, 0))
        if head.y < center[1]:
            center_directions.append((0, 1, 0))
        elif head.y > center[1]:
            center_directions.append((0, -1, 0))
        if head.z < center[2]:
            center_directions.append((0, 0, 1))
        elif head.z > center[2]:
            center_directions.append((0, 0, -1))
        return (
            center_directions
            if center_directions
            else [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        )
    else:
        if distance_to_center < 15:
            # Move away from center
            away_directions = []
            if head.x < center[0]:
                away_directions.append((-1, 0, 0))
            elif head.x > center[0]:
                away_directions.append((1, 0, 0))
            if head.y < center[1]:
                away_directions.append((0, -1, 0))
            elif head.y > center[1]:
                away_directions.append((0, 1, 0))
            if head.z < center[2]:
                away_directions.append((0, 0, -1))
            elif head.z > center[2]:
                away_directions.append((0, 0, 1))
            return (
                away_directions
                if away_directions
                else [
                    (1, 0, 0),
                    (-1, 0, 0),
                    (0, 1, 0),
                    (0, -1, 0),
                    (0, 0, 1),
                    (0, 0, -1),
                ]
            )
        elif distance_to_center > 30:
            # Move towards center
            center_directions = []
            if head.x < center[0]:
                center_directions.append((1, 0, 0))
            elif head.x > center[0]:
                center_directions.append((-1, 0, 0))
            if head.y < center[1]:
                center_directions.append((0, 1, 0))
            elif head.y > center[1]:
                center_directions.append((0, -1, 0))
            if head.z < center[2]:
                center_directions.append((0, 0, 1))
            elif head.z > center[2]:
                center_directions.append((0, 0, -1))
            return (
                center_directions
                if center_directions
                else [
                    (1, 0, 0),
                    (-1, 0, 0),
                    (0, 1, 0),
                    (0, -1, 0),
                    (0, 0, 1),
                    (0, 0, -1),
                ]
            )
        else:
            return [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def check_that_dead_end(
    pos: Tuple[int, int, int],
    obstacles: Set[Tuple[int, int, int]],
    head: Tuple[int, int, int],
) -> bool:
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    exit_count = 0
    for dx, dy, dz in directions:
        new_pos = (pos[0] + dx, pos[1] + dy, pos[2] + dz)
        if (new_pos not in obstacles) or new_pos == head:
            exit_count += 1
    return exit_count < 2


def score(dist: int, value: int) -> int:
    return (value**1.2) / dist


def find_nearest_food(
    head: Tuple[int, int, int], food_list: List[Tuple[int, int, int, int]], top_k=10
) -> List[Tuple[int, int, int]]:
    """Find top 3 nearest food items using Manhattan distance"""
    if not food_list:
        return []
    distances = [
        (score(manhattan_distance(head, f[:3]), f[-1]), f)
        for f in food_list
        if (f[-1] > 0)
    ]
    distances.sort(key=lambda x: x[0], reverse=True)  # Sort by  points / distance
    return [f[1] for f in distances[:top_k]]  # Return top k foods


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

        if g_score[current] >= 50:
            return []

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

    enemy_heads = set()

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
                    (1, 0, 0),
                    (-1, 0, 0),
                    (0, 1, 0),
                    (0, -1, 0),
                    (0, 0, 1),
                    (0, 0, -1),
                ]
            ]
            obstacles.update(possible_head_positions)
            enemy_heads.add((head.x, head.y, head.z))

    # Process each snake
    for snake in game_state.snakes:
        # print("processing snake", snake.id)
        if snake.status == "dead":
            snake_moves["snakes"].append({"id": snake.id, "direction": [0, 0, 0]})
            continue

        # Get snake head and body
        head = (snake.geometry[0].x, snake.geometry[0].y, snake.geometry[0].z)
        snake_body = {
            (segment.x, segment.y, segment.z) for segment in snake.geometry[1:]
        }

        # Collect and find nearest food
        # print("finding food")
        all_food = [(food.x, food.y, food.z, food.points) for food in game_state.food]

        # Validate food
        valid_food = []
        for f in all_food:
            food_pos = f[:3]
            if check_that_dead_end(food_pos, obstacles, head):
                continue

            if food_pos in obstacles:
                continue

            if check_that_dead_end(food_pos, obstacles, head):
                continue

            # Calculate distance to this snake's head
            distance_to_snake = manhattan_distance(head, food_pos)

            # Check if any enemy head is closer or equally close

            for enemy_head in enemy_heads:
                if (
                    manhattan_distance(enemy_head, food_pos) + get_offset(game_state)
                    <= distance_to_snake
                ):
                    break
            else:
                valid_food.append(f)

        nearest_food = find_nearest_food(head, valid_food, top_k=15)

        # Find best path to nearest food
        # print("finding path")
        best_path = None
        best_scr = 0
        for food in nearest_food:
            food_pos = food[:3]
            path = a_star_search(
                head, food_pos, obstacles, snake_body, game_state.mapSize
            )
            if not path:
                continue
            scr = score(len(path) - 1, food[-1])
            # print(food, scr, path)

            if path and (best_path is None or scr > best_scr):
                best_path = path
                best_scr = scr

        direction = [0, 0, 0]  # Default direction if no valid move found

        if best_path:
            # print("found path")
            next_pos = best_path[1]
            obstacles.add(next_pos)
            obstacles.add(best_path[-1])
            direction = [
                next_pos[0] - head[0],
                next_pos[1] - head[1],
                next_pos[2] - head[2],
            ]
        else:
            # Get strategic directions based on game state and position
            strategic_directions = get_directions(game_state, snake)
            random.shuffle(strategic_directions)

            # Add all other possible directions as fallback
            buffer_directions = [
                d
                for d in [
                    (1, 0, 0),
                    (-1, 0, 0),
                    (0, 1, 0),
                    (0, -1, 0),
                    (0, 0, 1),
                    (0, 0, -1),
                ]
                if d not in strategic_directions
            ]
            random.shuffle(buffer_directions)

            # Include old direction first for continuity
            old_direction = [
                snake.oldDirection.x,
                snake.oldDirection.y,
                snake.oldDirection.z,
            ]

            # Combine directions based on distance to center
            center = (
                game_state.mapSize.x // 2,
                game_state.mapSize.y // 2,
                game_state.mapSize.z // 2,
            )
            distance_to_center = manhattan_distance(head, center)

            if distance_to_center < 45:
                test_directions = (
                    [old_direction] + strategic_directions + buffer_directions
                )
            else:
                test_directions = strategic_directions + buffer_directions

            for test_dir in test_directions:
                test_pos = (
                    head[0] + test_dir[0],
                    head[1] + test_dir[1],
                    head[2] + test_dir[2],
                )
                if check_that_dead_end(test_pos, obstacles, head):
                    continue

                if is_valid_position(
                    test_pos, game_state.mapSize, obstacles, snake_body
                ):
                    obstacles.add(test_pos)
                    direction = list(test_dir)
                    break

        # write to file
        # print("writing to file")
        center = (
            game_state.mapSize.x // 2,
            game_state.mapSize.y // 2,
            game_state.mapSize.z // 2,
        )
        with open("log.txt", "a") as f:
            f.write(f"game_state: {game_state.turn}\n")
            f.write(f"snake: {snake.id}\n")
            f.write(f"head: {head}\n")
            f.write(f"direction: {direction}\n")
            f.write(
                f"next_point: {best_path[1] if best_path and len(best_path) > 1 else None}\n"
            )
            f.write(
                f"to_point: {best_path[-1] if best_path and len(best_path) >= 1 else None}\n"
            )
            f.write(f"distance: {len(best_path) if best_path else 0}\n")
            f.write(
                f"distance_manhattan: {manhattan_distance(head, best_path[-1]) if best_path else 0}\n"
            )
            f.write(f"distance_to_center: {manhattan_distance(head, center)}\n")
            f.write(f"\n")

        snake_moves["snakes"].append({"id": snake.id, "direction": direction})

    return snake_moves
