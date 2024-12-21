import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QTimer
import numpy as np
from source.data_objects import GameState
from source.utils import parse_game_state
import json
import time
import sys


class SnakeVisualizer:
    def __init__(self):
        # Create application if it doesn't exist
        self.app = QApplication.instance() or QApplication(sys.argv)

        # Create main widget and layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Create 3D view widget
        self.view = gl.GLViewWidget()
        self.view.setWindowTitle("Snake 3D Visualizer")
        self.view.resize(1600, 1200)
        self.layout.addWidget(self.view)

        # Create control buttons
        self.button_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.play_button = QPushButton("Play/Pause")
        self.next_button = QPushButton("Next")
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.play_button)
        self.button_layout.addWidget(self.next_button)
        self.layout.addLayout(self.button_layout)

        # Add grid for reference
        grid = gl.GLGridItem()
        self.view.addItem(grid)

        # Create legend
        self.turn_label = pg.TextItem(text="", color="k")

        # Store items for updating
        self.current_items = []

        # Animation state
        self.turns_data = []
        self.current_turn = 0
        self.is_playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

        # Connect button signals
        self.prev_button.clicked.connect(self.prev_frame)
        self.play_button.clicked.connect(self.toggle_play)
        self.next_button.clicked.connect(self.next_frame)

        # Show main widget
        self.main_widget.show()

    def update(self, game_state: GameState):
        """Обновляет визуализацию"""
        # Clear previous items
        for item in self.current_items:
            self.view.removeItem(item)
        self.current_items.clear()

        # Отображаем змей игрока
        for snake in game_state.snakes:
            if snake.status == "alive":
                points = np.array([[p.x, p.y, p.z] for p in snake.geometry])
                if len(points) > 0:
                    snake_scatter = gl.GLScatterPlotItem(
                        pos=points,
                        color=(0, 1, 0, 1),  # green
                        size=20,
                    )
                    self.view.addItem(snake_scatter)
                    self.current_items.append(snake_scatter)

        # Отображаем вражеских змей
        for enemy in game_state.enemies:
            if enemy.status == "alive":
                points = np.array([[p.x, p.y, p.z] for p in enemy.geometry])
                if len(points) > 0:
                    enemy_scatter = gl.GLScatterPlotItem(
                        pos=points,
                        color=(1, 0, 0, 1),  # red
                        size=20,
                    )
                    self.view.addItem(enemy_scatter)
                    self.current_items.append(enemy_scatter)

        # Отображаем еду
        if game_state.food:
            food_points = np.array([[f.x, f.y, f.z] for f in game_state.food])
            food_scatter = gl.GLScatterPlotItem(
                pos=food_points,
                color=(1, 1, 0, 1),  # yellow
                size=15,
            )
            self.view.addItem(food_scatter)
            self.current_items.append(food_scatter)

        # Отображаем специальную еду
        if game_state.specialFood:
            special_food_points = np.array(
                [[f.x, f.y, f.z] for f in game_state.specialFood]
            )
            special_food_scatter = gl.GLScatterPlotItem(
                pos=special_food_points,
                color=(1, 0, 1, 1),  # purple
                size=25,
            )
            self.view.addItem(special_food_scatter)
            self.current_items.append(special_food_scatter)

        # Update display
        self.view.update()
        QApplication.processEvents()

    def load_turns(self, turns_data):
        """Load turn data for playback"""
        self.turns_data = turns_data
        self.current_turn = 0
        if turns_data:
            self.update(turns_data[0])

    def next_frame(self):
        """Show next turn"""
        if self.current_turn < len(self.turns_data) - 1:
            self.current_turn += 1
            self.update(self.turns_data[self.current_turn])
        elif self.is_playing:
            self.toggle_play()  # Stop at end

    def prev_frame(self):
        """Show previous turn"""
        if self.current_turn > 0:
            self.current_turn -= 1
            self.update(self.turns_data[self.current_turn])

    def toggle_play(self):
        """Toggle play/pause state"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.timer.start(1000)  # 1 second between frames
        else:
            self.timer.stop()

    def run(self):
        """Start the Qt event loop"""
        return self.app.exec_()


def main():
    # Base path to the logs directory
    base_path = (
        "/Users/eaveselkov/shad/DatsNewWay/gameton_datsnewway/logs/snake3d-day1-3"
    )

    # Create visualizer
    visualizer = SnakeVisualizer()

    # Collect all game states first
    turns_data = []
    turn = 0
    while turn < 10:
        print(f"Loading turn: {turn}")
        turn_path = f"{base_path}/turn_{turn}/response.json"
        try:
            with open(turn_path, "r") as f:
                game_data = json.load(f)
                game_state = parse_game_state(game_data)
                turns_data.append(game_state)
        except FileNotFoundError:
            pass
        turn += 1

    print(f"Loaded {len(turns_data)} turns. Starting visualization...")

    # Load turns into visualizer
    visualizer.load_turns(turns_data)

    # Start the event loop
    visualizer.run()


if __name__ == "__main__":
    main()
