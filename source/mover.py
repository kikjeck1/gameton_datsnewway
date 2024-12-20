import random
from source.data_objects import Snake, Vector3D
from typing import List

def get_next_direction(current_direction: Vector3D, old_direction: Vector3D, geometry: List[Vector3D]) -> Vector3D:
    """
    Генерирует случайное направление, исключая обратное направление и столкновения с телом.
    """
    possible_directions = [
        Vector3D(1, 0, 0), Vector3D(-1, 0, 0),
        Vector3D(0, 1, 0), Vector3D(0, -1, 0),
        Vector3D(0, 0, 1), Vector3D(0, 0, -1)
    ]

    # Исключаем обратное направление
    backward_direction = Vector3D(-current_direction.x, -current_direction.y, -current_direction.z)
    possible_directions = [d for d in possible_directions if not (
        d.x == backward_direction.x and 
        d.y == backward_direction.y and 
        d.z == backward_direction.z
    )]

    head = geometry[0]
    while possible_directions:
        new_direction = random.choice(possible_directions)

        # Предполагаемая новая позиция головы
        new_head = Vector3D(
            head.x + new_direction.x,
            head.y + new_direction.y,
            head.z + new_direction.z
        )

        # Проверяем, чтобы новая позиция не пересекалась с телом
        if not any(pos.x == new_head.x and pos.y == new_head.y and pos.z == new_head.z for pos in geometry):
            return new_direction

        # Исключаем направление, которое привело бы к столкновению
        possible_directions.remove(new_direction)

    # Если не удалось найти направление, возвращаем текущее
    return current_direction

def get_next_state(snake: Snake) -> dict:
    """
    Рассчитывает следующий стейт змейки.
    Возвращает dict для совместимости с API.
    """
    if snake.status == "dead":
        # Если змейка мертва, возвращаем стейт без изменений
        return {
            "id": snake.id,
            "direction": [snake.direction.x, snake.direction.y, snake.direction.z],
            "oldDirection": [snake.oldDirection.x, snake.oldDirection.y, snake.oldDirection.z],
            "geometry": [[pos.x, pos.y, pos.z] for pos in snake.geometry],
            "deathCount": snake.deathCount,
            "status": snake.status,
            "reviveRemainMs": snake.reviveRemainMs,
        }

    # Генерация нового направления
    new_direction = get_next_direction(snake.direction, snake.oldDirection, snake.geometry)

    # Обновление геометрии змейки
    new_head = Vector3D(
        snake.geometry[0].x + new_direction.x,
        snake.geometry[0].y + new_direction.y,
        snake.geometry[0].z + new_direction.z
    )
    new_geometry = [new_head] + snake.geometry[:-1]

    return {
        "id": snake.id,
        "direction": [new_direction.x, new_direction.y, new_direction.z],
        "oldDirection": [snake.direction.x, snake.direction.y, snake.direction.z],
        "geometry": [[pos.x, pos.y, pos.z] for pos in new_geometry],
        "deathCount": snake.deathCount,
        "status": snake.status,
        "reviveRemainMs": snake.reviveRemainMs,
    }