import pygame
import random
import heapq

pygame.init()


screen = pygame.display.set_mode((1280, 640))

clock = pygame.time.Clock()
running = True
game_over = False


TILE_SIZE = 32
player_hp = 20

enemy_hp = 10
enemy_alive = True


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

import heapq

def get_neighbors(x, y):
    candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    result = []
    for nx, ny in candidates:
        if not is_wall(nx, ny):
            result.append((nx, ny))
    return result


import heapq

def get_neighbors(x, y):
    candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    result = []
    for nx, ny in candidates:
        if not is_wall(nx, ny):
            result.append((nx, ny))
    return result


def heuristic(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)  # Manhattan distance


def find_path(start_x, start_y, goal_x, goal_y):
    start = (start_x, start_y)
    goal = (goal_x, goal_y)

    open_heap = [(0, start)]          # (f_score, position)
    came_from = {}                     # tile -> tile we reached it from
    g_score = {start: 0}               # cost from start to each tile

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            # reconstruct path by walking backwards through came_from
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path  # includes start and goal

        for neighbor in get_neighbors(current[0], current[1]):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor[0], neighbor[1], goal_x, goal_y)
                came_from[neighbor] = current
                heapq.heappush(open_heap, (f_score, neighbor))

    return None  # no path exists


def heuristic(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)  # Manhattan distance


def find_path(start_x, start_y, goal_x, goal_y):
    start = (start_x, start_y)
    goal = (goal_x, goal_y)

    open_heap = [(0, start)]          # (f_score, position)
    came_from = {}                     # tile -> tile we reached it from
    g_score = {start: 0}               # cost from start to each tile

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            # reconstruct path by walking backwards through came_from
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path  # includes start and goal

        for neighbor in get_neighbors(current[0], current[1]):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor[0], neighbor[1], goal_x, goal_y)
                came_from[neighbor] = current
                heapq.heappush(open_heap, (f_score, neighbor))

    return None  # no path exists


player_x, player_y = room_center(actual_rooms[0])
enemy_x, enemy_y = room_center(actual_rooms[-1])


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_RIGHT:
                new_x = player_x + 1
                new_y = player_y
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    if enemy_hp <= 0:
                        enemy_alive = False
                elif not is_wall(new_x, new_y):
                    player_x = new_x

            elif event.key == pygame.K_LEFT:
                new_x = player_x - 1
                new_y = player_y
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    if enemy_hp <= 0:
                        enemy_alive = False
                elif not is_wall(new_x, new_y):
                    player_x = new_x

            elif event.key == pygame.K_UP:
                new_x = player_x
                new_y = player_y - 1
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    if enemy_hp <= 0:
                        enemy_alive = False
                elif not is_wall(new_x, new_y):
                    player_y = new_y

            elif event.key == pygame.K_DOWN:
                new_x = player_x
                new_y = player_y + 1
                if enemy_alive and new_x == enemy_x and new_y == enemy_y:
                    enemy_hp -= 5
                    if enemy_hp <= 0:
                        enemy_alive = False
                elif not is_wall(new_x, new_y):
                    player_y = new_y

            if enemy_alive:
                dx = player_x - enemy_x
                dy = player_y - enemy_y
                if abs(dx) + abs(dy) == 1:
                    player_hp -= 2
                    if player_hp <= 0:
                        game_over = True
                else:
                    path = find_path(enemy_x, enemy_y, player_x, player_y)
                    if path and len(path) > 1:
                        enemy_x, enemy_y = path[1]



              
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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()