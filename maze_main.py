# ============================================================
# Project Name:  Pygame Maze Game
# ============================================================

#
# PROGRAM DESCRIPTION
# ===================
# This program is a 2D maze game made with Python and Pygame. The player
# moves through a maze from the start tile to the exit tile while avoiding
# walls and following open paths. The game tracks how long the player
# takes to escape and saves the fastest time as a high score. Movement
# uses the arrow keys or WASD.

# Main features:
# - Maze drawn as a grid of colored tiles
# - Player that moves one tile at a time
# - Walls block movement
# - Start tile (green) and exit tile (red)
# - On‑screen timer
# - High‑score saved to a text file
# - Start screen and win screen
# - Optional difficulty levels

# Main classes:
# - Maze       — draws and stores the maze layout
# - Player     — handles movement and position
# - Timer      — tracks elapsed time
# - ScoreBoard — loads and saves best times

# Main functions:
# - draw_start_screen() — shows the title screen
# - draw_win_screen()   — shows the win screen and times
# - load_high_score()   — reads best time from file
# - save_high_score()   — writes new best time
# - main()              — runs the game loop


import pygame
import collections
import os
import sys

from maze_module import Maze, Player, Timer, ScoreBoard

# ============================================================
# CONSTANTS
# ============================================================
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
TILE_SIZE     = 40
FPS           = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED   = (200, 0, 0)
BLUE  = (50, 100, 200)
GRAY  = (180, 180, 180)

HIGH_SCORE_FILE = "high_score.txt"
MAZE_COLS = 15
MAZE_ROWS = 13
AI_MOVE_DELAY =200


# ============================================================
# FUNCTIONS
# ============================================================

def draw_start_screen(screen, font):
    #Display the title screen before the game begins.
    screen.fill(BLACK)

    title_font = pygame.font.SysFont("Arial", 48)
    title = title_font.render("Maze Game", True, WHITE)
    one_player = font.render("Press 1 for One Player", True, WHITE)
    two_player = font.render("Press 2 for Two Players", True, WHITE)
    ai_player = font.render("Press 3 to Race the AI", True, WHITE)
    controls = font.render("P1: WASD     P2: Arrow Keys", True, GRAY)

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 190)))
    screen.blit(one_player, one_player.get_rect(center=(SCREEN_WIDTH // 2, 270)))
    screen.blit(two_player, two_player.get_rect(center=(SCREEN_WIDTH // 2, 315)))
    screen.blit(ai_player, ai_player.get_rect(center=(SCREEN_WIDTH // 2, 360)))
    screen.blit(controls, controls.get_rect(center=(SCREEN_WIDTH // 2, 425)))
    pygame.display.flip()


def draw_win_screen(screen, font, elapsed_time, best_time, winner_text):
    #Display the win screen showing the player's time and best time.
    screen.fill(BLACK)

    title_font = pygame.font.SysFont("Arial", 48)
    title = title_font.render(winner_text, True, GREEN)
    time_text = font.render(f"Time: {elapsed_time:.2f} seconds", True, WHITE)

    if best_time is None:
        best_text = font.render("Race mode does not save best times", True, WHITE)
    elif best_time == float("inf"):
        best_text = font.render("Best time: none yet", True, WHITE)
    else:
        best_text = font.render(f"Best time: {best_time:.2f} seconds", True, WHITE)

    restart = font.render("Press 1, 2, or 3 to play again, ESC to quit", True, GRAY)

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 180)))
    screen.blit(time_text, time_text.get_rect(center=(SCREEN_WIDTH // 2, 270)))
    screen.blit(best_text, best_text.get_rect(center=(SCREEN_WIDTH // 2, 315)))
    screen.blit(restart, restart.get_rect(center=(SCREEN_WIDTH // 2, 390)))
    pygame.display.flip()


def load_high_score(filepath):
    #Read the best time from a text file. Returns float('inf') if missing.#
    if not os.path.exists(filepath):
        return float("inf")

    try:
        with open(filepath, "r") as file:
            return float(file.read().strip())
    except (OSError, ValueError):
        return float("inf")


def save_high_score(filepath, time_value):
    #Write a new best time to the text file.
    with open(filepath, "w") as file:
        file.write(str(time_value))


def get_next_step(maze, start_pos, goal_pos):
    #Return the next position on the shortest path from start_pos to goal_pos.
    queue = collections.deque([start_pos])
    previous = {start_pos: None}
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        col, row = queue.popleft()

        if (col, row) == goal_pos:
            break

        for change_col, change_row in directions:
            next_pos = (col + change_col, row + change_row)

            if next_pos not in previous and not maze.is_wall(next_pos[0], next_pos[1]):
                previous[next_pos] = (col, row)
                queue.append(next_pos)

    if goal_pos not in previous:
        return start_pos

    current_pos = goal_pos
    while previous[current_pos] != start_pos:
        current_pos = previous[current_pos]

    return current_pos


# ============================================================
# MAIN GAME LOOP
# ============================================================

def main():
    #Main game loop.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28)

    game_state = "start"
    maze = Maze(cols=MAZE_COLS, rows=MAZE_ROWS, tile_size=TILE_SIZE)
    player1 = Player(
        start_col=maze.start_pos[0],
        start_row=maze.start_pos[1],
        tile_size=TILE_SIZE,
        color=BLUE,
    )
    player2 = None
    timer = Timer()
    board = ScoreBoard(HIGH_SCORE_FILE)
    elapsed_time = 0
    winner_text = "You Escaped!"
    game_mode = "solo"
    last_ai_move_time = 0

    def reset_game(mode):
        nonlocal maze, player1, player2, timer, elapsed_time
        nonlocal winner_text, game_mode, last_ai_move_time
        game_mode = mode
        maze = Maze(cols=MAZE_COLS, rows=MAZE_ROWS, tile_size=TILE_SIZE)
        player1 = Player(
            start_col=maze.start_pos[0],
            start_row=maze.start_pos[1],
            tile_size=TILE_SIZE,
            color=BLUE,
        )
        player2 = None
        if game_mode in ("two_player", "ai"):
            player2 = Player(
                start_col=maze.exit_pos[0],
                start_row=maze.exit_pos[1],
                tile_size=TILE_SIZE,
                color=(240, 180, 30),
            )
        timer = Timer()
        timer.start()
        elapsed_time = 0
        winner_text = "You Escaped!"
        last_ai_move_time = pygame.time.get_ticks()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if game_state == "start":
                    if event.key == pygame.K_1:
                        reset_game("solo")
                        game_state = "playing"
                    elif event.key == pygame.K_2:
                        reset_game("two_player")
                        game_state = "playing"
                    elif event.key == pygame.K_3:
                        reset_game("ai")
                        game_state = "playing"

                elif game_state == "playing":
                    if event.key == pygame.K_w:
                        player1.move("up", maze)
                    elif event.key == pygame.K_s:
                        player1.move("down", maze)
                    elif event.key == pygame.K_a:
                        player1.move("left", maze)
                    elif event.key == pygame.K_d:
                        player1.move("right", maze)

                    if game_mode == "solo":
                        if event.key == pygame.K_UP:
                            player1.move("up", maze)
                        elif event.key == pygame.K_DOWN:
                            player1.move("down", maze)
                        elif event.key == pygame.K_LEFT:
                            player1.move("left", maze)
                        elif event.key == pygame.K_RIGHT:
                            player1.move("right", maze)
                    elif game_mode == "two_player" and player2 is not None:
                        if event.key == pygame.K_UP:
                            player2.move("up", maze)
                        elif event.key == pygame.K_DOWN:
                            player2.move("down", maze)
                        elif event.key == pygame.K_LEFT:
                            player2.move("left", maze)
                        elif event.key == pygame.K_RIGHT:
                            player2.move("right", maze)

                elif game_state == "win":
                    if event.key == pygame.K_1:
                        reset_game("solo")
                        game_state = "playing"
                    elif event.key == pygame.K_2:
                        reset_game("two_player")
                        game_state = "playing"
                    elif event.key == pygame.K_3:
                        reset_game("ai")
                        game_state = "playing"

        if game_state == "start":
            draw_start_screen(screen, font)

        elif game_state == "playing":
            if game_mode == "ai" and player2 is not None:
                current_time = pygame.time.get_ticks()
                if current_time - last_ai_move_time >= AI_MOVE_DELAY:
                    next_col, next_row = get_next_step(maze, player2.get_pos(), maze.start_pos)
                    player2.col = next_col
                    player2.row = next_row
                    last_ai_move_time = current_time

            if player1.get_pos() == maze.exit_pos:
                elapsed_time = timer.stop()
                if game_mode in ("two_player", "ai"):
                    winner_text = "Player 1 Wins!"
                else:
                    winner_text = "You Escaped!"
                if game_mode == "solo" and board.is_record(elapsed_time):
                    board.save(elapsed_time)
                game_state = "win"
                continue

            if game_mode in ("two_player", "ai") and player2 is not None and player2.get_pos() == maze.start_pos:
                elapsed_time = timer.stop()
                winner_text = "AI Wins!" if game_mode == "ai" else "Player 2 Wins!"
                game_state = "win"
                continue

            screen.fill(WHITE)
            maze.draw(screen)
            player1.draw(screen)
            if player2 is not None:
                player2.draw(screen)

            time_text = font.render(f"Time: {timer.get_elapsed():.2f}", True, BLACK)
            screen.blit(time_text, (620, 20))

            if game_mode == "solo":
                if board.best_time == float("inf"):
                    best_text = font.render("Best: --", True, BLACK)
                else:
                    best_text = font.render(f"Best: {board.best_time:.2f}", True, BLACK)
                screen.blit(best_text, (620, 55))
            else:
                p1_text = font.render("P1 to red", True, BLUE)
                if game_mode == "ai":
                    p2_text = font.render("AI to green", True, (180, 120, 0))
                else:
                    p2_text = font.render("P2 to green", True, (180, 120, 0))
                screen.blit(p1_text, (620, 55))
                screen.blit(p2_text, (620, 90))

            pygame.display.flip()

        elif game_state == "win":
            best_time = board.best_time if game_mode == "solo" else None
            draw_win_screen(screen, font, elapsed_time, best_time, winner_text)

    pygame.quit()
    sys.exit()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
