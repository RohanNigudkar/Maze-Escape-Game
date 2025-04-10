import pygame
import random

pygame.init()

GRID_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = 15, 15
SCREEN_WIDTH, SCREEN_HEIGHT = GRID_SIZE * GRID_WIDTH, GRID_SIZE * GRID_HEIGHT

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
TEAL = (0, 128, 128)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Escape Game")

walls = []
exit_position = (GRID_WIDTH - 1, GRID_HEIGHT - 1)

def generate_maze_with_multiple_solutions():
    global walls
    walls = []
    
    maze_grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    start_x, start_y = 0, 0
    maze_grid[start_x][start_y] = 0

    def carve_passages_from(x, y):
        directions = [(0, -2), (0, 2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and maze_grid[nx][ny] == 1:
                maze_grid[x + dx // 2][y + dy // 2] = 0
                maze_grid[nx][ny] = 0
                carve_passages_from(nx, ny)

    carve_passages_from(start_x, start_y)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if maze_grid[x][y] == 1:
                walls.append((x, y))

    if exit_position in walls:
        walls.remove(exit_position)

    extra_paths = 15
    for _ in range(extra_paths):
        x = random.randint(1, GRID_WIDTH - 2)
        y = random.randint(1, GRID_HEIGHT - 2)
        if (x, y) in walls and (x, y) != (0, 0) and (x, y) != exit_position:
            walls.remove((x, y))

def draw_maze():
    screen.fill(WHITE)
    for wall in walls:
        pygame.draw.rect(screen, BLACK, pygame.Rect(wall[0] * GRID_SIZE, wall[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, GREEN, pygame.Rect(exit_position[0] * GRID_SIZE, exit_position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class AIAgent:
    def __init__(self, color):
        self.position = (0, 0)
        self.color = color
        self.visited = set()
        self.path_stack = [(0, 0)]
        self.move_delay = 200
        self.last_move_time = pygame.time.get_ticks()

    def reset(self):
        self.position = (0, 0)
        self.visited.clear()
        self.path_stack = [(0, 0)]
        self.last_move_time = pygame.time.get_ticks()

    def heuristic(self, position):
        x, y = position
        ex, ey = exit_position
        return abs(x - ex) + abs(y - ey)

    def move_towards_exit(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_delay:
            x, y = self.position
            directions = []
            if x < GRID_WIDTH - 1 and (x + 1, y) not in walls and (x + 1, y) not in self.visited:
                directions.append((x + 1, y))
            if x > 0 and (x - 1, y) not in walls and (x - 1, y) not in self.visited:
                directions.append((x - 1, y))
            if y < GRID_HEIGHT - 1 and (x, y + 1) not in walls and (x, y + 1) not in self.visited:
                directions.append((x, y + 1))
            if y > 0 and (x, y - 1) not in walls and (x, y - 1) not in self.visited:
                directions.append((x, y - 1))
            if directions:
                best_move = min(directions, key=self.heuristic)
                self.position = best_move
                self.visited.add(self.position)
                self.path_stack.append(self.position)
            else:
                if self.path_stack:
                    self.path_stack.pop()
                    if self.path_stack:
                        self.position = self.path_stack[-1]
            self.last_move_time = current_time

def game_loop():
    generate_maze_with_multiple_solutions()
    ai_agent = AIAgent(TEAL)
    player_position = [0, 0]
    clock = pygame.time.Clock()
    running = True
    player_wins = False
    ai_wins = False

    while running:
        draw_maze()
        pygame.draw.rect(screen, ai_agent.color, pygame.Rect(ai_agent.position[0] * GRID_SIZE, ai_agent.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, ORANGE, pygame.Rect(player_position[0] * GRID_SIZE, player_position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.display.flip()

        ai_agent.move_towards_exit()
        if ai_agent.position == exit_position:
            ai_wins = True
            print("AI Wins!")
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                x, y = player_position
                if event.key == pygame.K_UP and y > 0 and (x, y - 1) not in walls:
                    y -= 1
                elif event.key == pygame.K_DOWN and y < GRID_HEIGHT - 1 and (x, y + 1) not in walls:
                    y += 1
                elif event.key == pygame.K_LEFT and x > 0 and (x - 1, y) not in walls:
                    x -= 1
                elif event.key == pygame.K_RIGHT and x < GRID_WIDTH - 1 and (x + 1, y) not in walls:
                    x += 1
                player_position = [x, y]

        if tuple(player_position) == exit_position:
            player_wins = True
            print("Player Wins!")
            running = False

        clock.tick(30)

    font = pygame.font.SysFont(None, 55)
    screen.fill(WHITE)
    if player_wins:
        text = font.render("Player Wins!", True, GREEN)
    elif ai_wins:
        text = font.render("AI Wins!", True, RED)
    screen.blit(text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()

game_loop()
