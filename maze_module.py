# ============================================================
# Project Name:  Pygame Maze Game — Module File
# ============================================================


# maze_module.py
# ==============
# This file contains the classes used by the main maze game:
# - Maze       : stores the maze layout and draws it
# - Player     : handles movement and drawing
# - Timer      : tracks elapsed time
# - ScoreBoard : loads and saves the best time


import pygame
import os
import random


# ============================================================
# CLASS: Maze
# ============================================================

class Maze:
    # This class stores the maze grid and draws it to the screen.
    # In the grid, 1 means wall and 0 means open path.

    def __init__(self, cols, rows, tile_size):
        # Save the maze size and tile size so the other methods can use them.
        self.cols = cols
        self.rows = rows
        self.tile_size = tile_size
        self.grid = []              # 0 = path, 1 = wall

        # The player starts near the top left.
        # The exit is near the bottom right.
        self.start_pos = (1, 1)
        self.exit_pos = (cols - 2, rows - 2)

        # This makes the random maze when the Maze object is created.
        self.grid = self._create_layout()

    def _create_layout(self):
        # Create a random maze layout that fits the requested size.
        # The maze starts as all walls.
        layout = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

        # The stack keeps track of where the maze generator has been.
        # It starts at the start position.
        stack = [self.start_pos]
        layout[self.start_pos[1]][self.start_pos[0]] = 0

        while stack:
            # Look at the last square added to the stack.
            col, row = stack[-1]
            neighbors = []

            # Check the squares two spaces away.
            # Moving two spaces leaves a wall between the current square
            # and the next square that can be knocked down.
            for change_col, change_row in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                next_col = col + change_col
                next_row = row + change_row

                # Only use the square if it is inside the maze and still a wall.
                if (
                    1 <= next_col < self.cols - 1
                    and 1 <= next_row < self.rows - 1
                    and layout[next_row][next_col] == 1
                ):
                    neighbors.append((next_col, next_row, change_col, change_row))

            if neighbors:
                # Pick one random neighbor and open the path to it.
                next_col, next_row, change_col, change_row = random.choice(neighbors)
                wall_col = col + change_col // 2
                wall_row = row + change_row // 2
                layout[wall_row][wall_col] = 0
                layout[next_row][next_col] = 0
                stack.append((next_col, next_row))
            else:
                # If there are no neighbors left, go back one step.
                stack.pop()

        # A few extra gaps make races less stuck in one hallway.
        for row in range(2, self.rows - 2):
            for col in range(2, self.cols - 2):
                if layout[row][col] == 1 and random.random() < 0.08:
                    layout[row][col] = 0

        # Make sure the start and exit are open no matter what.
        layout[self.start_pos[1]][self.start_pos[0]] = 0
        layout[self.exit_pos[1]][self.exit_pos[0]] = 0
        return layout

    def draw(self, screen):
        # Draw each tile as a colored rectangle.
        wall_color = (40, 40, 40)
        path_color = (235, 235, 235)
        start_color = (0, 200, 0)
        exit_color = (200, 0, 0)

        for row in range(self.rows):
            for col in range(self.cols):
                # Make a rectangle for this tile.
                rect = pygame.Rect(
                    col * self.tile_size,
                    row * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                )

                # Pick the color based on what kind of tile it is.
                if (col, row) == self.start_pos:
                    color = start_color
                elif (col, row) == self.exit_pos:
                    color = exit_color
                elif self.grid[row][col] == 1:
                    color = wall_color
                else:
                    color = path_color

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (160, 160, 160), rect, 1)

    def is_wall(self, col, row):
        # Return True if the tile at (col, row) is a wall.
        # Anything outside the maze also counts as a wall.
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return True
        return self.grid[row][col] == 1


# ============================================================
# CLASS: Player
# ============================================================

class Player:
    # This class represents one player.
    # It stores the player's grid location and color.

    def __init__(self, start_col, start_row, tile_size, color=(50, 100, 200)):
        self.col = start_col
        self.row = start_row
        self.tile_size = tile_size
        self.color = color

    def move(self, direction, maze):
        # Move one tile in the given direction if there is not a wall.
        change_col = 0
        change_row = 0

        # Decide how the row or column should change.
        if direction == "up":
            change_row = -1
        elif direction == "down":
            change_row = 1
        elif direction == "left":
            change_col = -1
        elif direction == "right":
            change_col = 1

        new_col = self.col + change_col
        new_row = self.row + change_row

        # Only move if the new square is not a wall.
        if not maze.is_wall(new_col, new_row):
            self.col = new_col
            self.row = new_row

    def draw(self, screen):
        # Draw the player as a smaller rectangle inside the tile.
        padding = 6
        rect = pygame.Rect(
            self.col * self.tile_size + padding,
            self.row * self.tile_size + padding,
            self.tile_size - padding * 2,
            self.tile_size - padding * 2,
        )
        pygame.draw.rect(screen, self.color, rect)

    def get_pos(self):
        # Return the player's (col, row) position.
        return (self.col, self.row)


# ============================================================
# CLASS: Timer
# ============================================================

class Timer:
    # This class tracks how long the game has been running.

    def __init__(self):
        self.start_time = 0
        self.running = False

    def start(self):
        # Start the timer by saving the current pygame time.
        self.start_time = pygame.time.get_ticks()
        self.running = True

    def get_elapsed(self):
        # Return elapsed time in seconds.
        if not self.running:
            return 0
        return (pygame.time.get_ticks() - self.start_time) / 1000

    def stop(self):
        # Stop the timer and return the final time.
        elapsed = self.get_elapsed()
        self.running = False
        return elapsed


# ============================================================
# CLASS: ScoreBoard
# ============================================================

class ScoreBoard:
    # This class loads and saves the best time from a text file.

    def __init__(self, filepath):
        self.filepath = filepath
        self.best_time = self.load()

    def load(self):
        # Read the best time from the file.
        # If there is no file yet, return infinity so any real time is better.
        if not os.path.exists(self.filepath):
            return float('inf')

        try:
            with open(self.filepath, "r") as file:
                return float(file.read().strip())
        except (OSError, ValueError):
            return float('inf')

    def save(self, time_value):
        # Write a new best time to the file.
        with open(self.filepath, "w") as file:
            file.write(str(time_value))
        self.best_time = time_value

    def is_record(self, time_value):
        # Return True if the new time is better than the old best time.
        return time_value < self.best_time
