import pygame
import random
import heapq
import requests

pygame.init()


SCREEN_WIDTH = 1280
MAP_PIXEL_HEIGHT = 640
LOG_HEIGHT = 110
screen = pygame.display.set_mode((SCREEN_WIDTH, MAP_PIXEL_HEIGHT + LOG_HEIGHT))

clock = pygame.time.Clock()
running = True
game_over = False
won = False  # True if the game ended by killing the enemy, False if the player died
run_saved = False  # so we only save the run once, not every frame after death
cached_recent_runs = []  # fetched once per game-over, not every frame


TILE_SIZE = 32
player_hp = 20

enemy_hp = 10
enemy_alive = True
enemies_killed = 0

MAX_LOG_MESSAGES = 5
message_log = []


def add_message(text):
    message_log.append(text)
    if len(message_log) > MAX_LOG_MESSAGES:
        message_log.pop(0)


class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def split_rect(rect):
    split_horizontal = random.choice([True, False])

    if split_horizontal:
        split_point = random.randint(rect.height // 3, rect.height * 2 // 3)
        top = Rect(rect.x, rect.y, rect.width, split_point)
        bottom = Rect(rect.x, rect.y + split_point, rect.width, rect.height - split_point)
        return top, bottom
    else:
        split_point = random.randint(rect.width // 3, rect.width * 2 // 3)
        left = Rect(rect.x, rect.y, split_point, rect.height)
        right = Rect(rect.x + split_point, rect.y, rect.width - split_point, rect.height)
        return left, right


def split_recursive(rect, depth):
    if depth == 0 or rect.width < 6 or rect.height < 6:
        return [rect]
    piece_a, piece_b = split_rect(rect)
    return split_recursive(piece_a, depth - 1) + split_recursive(piece_b, depth - 1)


def rect_to_room(rect):
    margin = 1
    room_x = rect.x + margin
    room_y = rect.y + margin
    room_width = rect.width - margin * 2
    room_height = rect.height - margin * 2
    return Rect(room_x, room_y, room_width, room_height)


def room_center(room):
    center_x = room.x + room.width // 2
    center_y = room.y + room.height // 2
    return center_x, center_y


def carve_corridor(grid, x1, y1, x2, y2):
    x_start = min(x1, x2)
    x_end = max(x1, x2)
    for x in range(x_start, x_end + 1):
        grid[y1][x] = "0"

    y_start = min(y1, y2)
    y_end = max(y1, y2)
    for y in range(y_start, y_end + 1):
        grid[y][x2] = "0"


def rooms_to_map(rooms, map_width, map_height):
    grid = []
    for y in range(map_height):
        row = ["1"] * map_width
        grid.append(row)

    for room in rooms:
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                grid[y][x] = "0"

    for i in range(len(rooms) - 1):
        x1, y1 = room_center(rooms[i])
        x2, y2 = room_center(rooms[i + 1])
        carve_corridor(grid, x1, y1, x2, y2)

    result = []
    for row in grid:
        result.append("".join(row))
    return result


MAP_WIDTH = 40
MAP_HEIGHT = 20

whole_map = Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
pieces = split_recursive(whole_map, 3)
actual_rooms = []
for piece in pieces:
    actual_rooms.append(rect_to_room(piece))

LEVEL_MAP = rooms_to_map(actual_rooms, MAP_WIDTH, MAP_HEIGHT)


def is_wall(grid_x, grid_y):
    if grid_y < 0 or grid_y >= len(LEVEL_MAP):
        return True
    row = LEVEL_MAP[grid_y]
    if grid_x < 0 or grid_x >= len(row):
        return True
    return row[grid_x] == "1"


def get_neighbors(x, y):
    candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    result = []
    for nx, ny in candidates:
        if not is_wall(nx, ny):
            result.append((nx, ny))
    return result


def heuristic(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def find_path(start_x, start_y, goal_x, goal_y):
    start = (start_x, start_y)
    goal = (goal_x, goal_y)

    open_heap = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for neighbor in get_neighbors(current[0], current[1]):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor[0], neighbor[1], goal_x, goal_y)
                came_from[neighbor] = current
                heapq.heappush(open_heap, (f_score, neighbor))

    return None


# ---------------------------------------------------------------------------
# Persistence (Phase 5): the game now talks to the FastAPI backend over
# HTTP instead of writing to SQLite directly. The API (api.py) owns the
# database; this client just sends/receives JSON.
# ---------------------------------------------------------------------------

API_URL = "http://127.0.0.1:8000"


def save_run(enemies_killed_count, survived):
    try:
        requests.post(f"{API_URL}/runs", json={
            "enemies_killed": enemies_killed_count,
            "survived": survived
        })
    except requests.exceptions.ConnectionError:
        print("Warning: couldn't reach the API, run not saved.")


def get_recent_runs(limit=5):
    try:
        response = requests.get(f"{API_URL}/runs", params={"limit": limit})
        return [(r["enemies_killed"], r["survived"], r["date"]) for r in response.json()]
    except requests.exceptions.ConnectionError:
        return []


player_x, player_y = room_center(actual_rooms[0])
enemy_x, enemy_y = room_center(actual_rooms[-1])

font = pygame.font.SysFont("consolas", 20)
font_small = pygame.font.SysFont("consolas", 16)


def draw_message_log(surface):
    log_y = MAP_PIXEL_HEIGHT
    pygame.draw.rect(surface, (15, 15, 20), (0, log_y, SCREEN_WIDTH, LOG_HEIGHT))
    pygame.draw.line(surface, (60, 60, 70), (0, log_y), (SCREEN_WIDTH, log_y), 2)

    y_offset = log_y + 8
    for message in message_log:
        line = font_small.render(message, True, (200, 200, 210))
        surface.blit(line, (10, y_offset))
        y_offset += 20


def draw_hp_bar(surface):
    text = font_small.render(f"HP: {player_hp} / 20", True, (230, 230, 230))
    surface.blit(text, (10, 5))


def draw_game_over(surface):
    overlay = pygame.Surface((SCREEN_WIDTH, MAP_PIXEL_HEIGHT + LOG_HEIGHT))
    overlay.set_alpha(210)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    if won:
        title = font.render("FLOOR CLEARED — press R for a new dungeon", True, (120, 220, 140))
    else:
        title = font.render("YOU DIED — press R to play again", True, (255, 90, 90))
    surface.blit(title, (40, 40))

    subtitle = font_small.render(f"Enemies killed this run: {enemies_killed}", True, (230, 230, 230))
    surface.blit(subtitle, (40, 80))

    header = font_small.render("Recent runs:", True, (200, 200, 200))
    surface.blit(header, (40, 120))

    y_offset = 150
    for kills, survived, date in cached_recent_runs:
        result_text = "Survived" if survived else "Died"
        line = font_small.render(f"{date} — {result_text} — {kills} kills", True, (180, 180, 180))
        surface.blit(line, (40, y_offset))
        y_offset += 24


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_r:
            # restart: regenerate a new dungeon and reset state
            pieces = split_recursive(Rect(0, 0, MAP_WIDTH, MAP_HEIGHT), 3)
            actual_rooms = [rect_to_room(p) for p in pieces]
            LEVEL_MAP = rooms_to_map(actual_rooms, MAP_WIDTH, MAP_HEIGHT)
            player_x, player_y = room_center(actual_rooms[0])
            enemy_x, enemy_y = room_center(actual_rooms[-1])
            player_hp = 20
            enemy_hp = 10
            enemy_alive = True
            enemies_killed = 0
            game_over = False
            won = False
            run_saved = False
            message_log.clear()
            add_message("A new dungeon appears.")

        if event.type == pygame.KEYDOWN and not game_over:
            player_acted = event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d)

            if event.key == pygame.K_d:
                new_x = player_x + 1
                new_y = player_y
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    add_message(f"You hit the enemy for 5. (enemy HP: {max(enemy_hp,0)})")
                    if enemy_hp <= 0:
                        enemy_alive = False
                        enemies_killed += 1
                        add_message("You defeated the enemy!")
                elif not is_wall(new_x, new_y):
                    player_x = new_x
                    add_message("You moved right.")

            elif event.key == pygame.K_a:
                new_x = player_x - 1
                new_y = player_y
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    add_message(f"You hit the enemy for 5. (enemy HP: {max(enemy_hp,0)})")
                    if enemy_hp <= 0:
                        enemy_alive = False
                        enemies_killed += 1
                        add_message("You defeated the enemy!")
                elif not is_wall(new_x, new_y):
                    player_x = new_x
                    add_message("You moved left.")

            elif event.key == pygame.K_w:
                new_x = player_x
                new_y = player_y - 1
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    add_message(f"You hit the enemy for 5. (enemy HP: {max(enemy_hp,0)})")
                    if enemy_hp <= 0:
                        enemy_alive = False
                        enemies_killed += 1
                        add_message("You defeated the enemy!")
                elif not is_wall(new_x, new_y):
                    player_y = new_y
                    add_message("You moved up.")

            elif event.key == pygame.K_s:
                new_x = player_x
                new_y = player_y + 1
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    add_message(f"You hit the enemy for 5. (enemy HP: {max(enemy_hp,0)})")
                    if enemy_hp <= 0:
                        enemy_alive = False
                        enemies_killed += 1
                        add_message("You defeated the enemy!")
                elif not is_wall(new_x, new_y):
                    player_y = new_y
                    add_message("You moved down.")

            # killing the enemy ends the run as a win
            if not enemy_alive and not game_over:
                game_over = True
                won = True

            # the enemy only gets a turn if the player actually did something (a real WASD press)
            if player_acted and enemy_alive:
                dx = player_x - enemy_x
                dy = player_y - enemy_y
                if abs(dx) + abs(dy) == 1:
                    player_hp -= 2
                    add_message(f"The enemy hits you for 2. (your HP: {max(player_hp,0)})")
                    if player_hp <= 0:
                        game_over = True
                else:
                    path = find_path(enemy_x, enemy_y, player_x, player_y)
                    if path and len(path) > 1:
                        enemy_x, enemy_y = path[1]
                        add_message("The enemy moves closer.")

    # save the run exactly once, right when the game transitions to game_over
    if game_over and not run_saved:
        save_run(enemies_killed, survived=won)
        cached_recent_runs = get_recent_runs(5)
        run_saved = True

    screen.fill((30, 30, 40))
    for grid_y, row in enumerate(LEVEL_MAP):
        for grid_x, cell in enumerate(row):
            if cell == "1":
                color = (60, 60, 70)
            else:
                color = (35, 35, 45)
            pygame.draw.rect(screen, color, (TILE_SIZE * grid_x, TILE_SIZE * grid_y, TILE_SIZE, TILE_SIZE))

    pygame.draw.rect(screen, (80, 200, 255), (TILE_SIZE * player_x, TILE_SIZE * player_y, TILE_SIZE, TILE_SIZE))
    if enemy_alive:
        pygame.draw.rect(screen, (220, 60, 60), (TILE_SIZE * enemy_x, TILE_SIZE * enemy_y, TILE_SIZE, TILE_SIZE))

    draw_hp_bar(screen)
    draw_message_log(screen)

    if game_over:
        draw_game_over(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
