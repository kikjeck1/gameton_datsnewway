import pygame
import json
from pathlib import Path
from typing import Dict, List, Optional
from source.data_objects import GameState, Vector2D, Transport, Enemy, Anomaly, Bounty
from source.utils import parse_game_state

class Visualizer:
    # Colors for different game objects
    COLORS = {
        'background': (0, 0, 0),
        'transport': (0, 255, 0),
        'enemy': (255, 0, 0),
        'anomaly': (128, 0, 128),
        'bounty': (255, 215, 0),
        'text': (255, 255, 255)
    }

    def __init__(self, window_size: tuple[int, int] = (800, 800)):
        pygame.init()
        self.window_size = window_size
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Game Visualizer")
        self.clock = pygame.time.Clock()
        self.scale_factor = 1.0
        self.font = pygame.font.Font(None, 24)

    def _scale_coordinates(self, x: float, y: float, map_size: Vector2D) -> tuple[int, int]:
        """Convert game coordinates to screen coordinates"""
        scale_x = self.window_size[0] / map_size.x
        scale_y = self.window_size[1] / map_size.y
        self.scale_factor = min(scale_x, scale_y)
        
        screen_x = int(x * self.scale_factor)
        screen_y = int(y * self.scale_factor)
        return screen_x, screen_y

    def _draw_object(self, pos_x: float, pos_y: float, radius: float, color: tuple, 
                    map_size: Vector2D, label: Optional[str] = None):
        """Draw a game object as a circle with optional label"""
        screen_x, screen_y = self._scale_coordinates(pos_x, pos_y, map_size)
        screen_radius = int(radius * self.scale_factor)
        
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), screen_radius)
        
        if label:
            text = self.font.render(label, True, self.COLORS['text'])
            text_rect = text.get_rect(center=(screen_x, screen_y - screen_radius - 10))
            self.screen.blit(text, text_rect)

    def draw_game_state(self, game_state: GameState):
        """Draw current game state"""
        self.screen.fill(self.COLORS['background'])

        # Draw bounties
        for bounty in game_state.bounties:
            self._draw_object(bounty.x, bounty.y, bounty.radius, 
                            self.COLORS['bounty'], game_state.mapSize, 
                            f"+{bounty.points}")

        # Draw anomalies
        for anomaly in game_state.anomalies:
            self._draw_object(anomaly.x, anomaly.y, anomaly.radius,
                            self.COLORS['anomaly'], game_state.mapSize)

        # Draw enemies
        for enemy in game_state.enemies:
            self._draw_object(enemy.x, enemy.y, game_state.transportRadius,
                            self.COLORS['enemy'], game_state.mapSize,
                            f"HP:{enemy.health}")

        # Draw transports
        for transport in game_state.transports:
            self._draw_object(transport.x, transport.y, game_state.transportRadius,
                            self.COLORS['transport'], game_state.mapSize,
                            f"HP:{transport.health}")

        pygame.display.flip()

    def replay_from_logs(self, round_dir: Path):
        """Replay a recorded game round from logs"""
        move_number = 1
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        move_number += 1
                    elif event.key == pygame.K_LEFT:
                        move_number = max(1, move_number - 1)
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            response_file = round_dir / f"move_{move_number}_response.json"
            if response_file.exists():
                with open(response_file, 'r') as f:
                    game_data = json.load(f)
                    game_state = parse_game_state(game_data)
                    self.draw_game_state(game_state)
            
            self.clock.tick(30)

        pygame.quit()

    def run_realtime(self, game_state: GameState):
        """Update visualization with current game state"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        self.draw_game_state(game_state)
        self.clock.tick(30)
        return True
