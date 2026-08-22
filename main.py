import pygame
import random
pygame.init()


screen = pygame.display.set_mode((640, 480))

clock = pygame.time.Clock()
running = True
game_over = False



TILE_SIZE = 32
player_x = 3  #3 tiles over , 3 tiles down
player_y = 3
player_hp = 20

enemy_x = 7
enemy_y = 3
enemy_hp = 10
enemy_alive = True




LEVEL_MAP = [                    # wall = 1, floor = 0
    "1111111111",
    "1000000001",
    "1011111001",
    "1000000001",
    "1111111111",
]

def is_wall(grid_x, grid_y):
    row = LEVEL_MAP[grid_y]
    return row[grid_x] == "1"


class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def split_rect(rect):
    # decide split direction randomly
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
        return [rect]  # too small or done splitting — this is a final leaf

    piece_a, piece_b = split_rect(rect)
    return split_recursive(piece_a, depth - 1) + split_recursive(piece_b, depth - 1)


def rect_to_room(rect):
    margin = 1
    room_x = rect.x + margin
    room_y = rect.y + margin
    room_width = rect.width - margin * 2
    room_height = rect.height - margin * 2
    return Rect(room_x, room_y, room_width, room_height)


def rooms_to_map(rooms, map_width, map_height):
    # start with a grid that's entirely walls
    grid = []
    for y in range(map_height):
        row = ["1"] * map_width
        grid.append(row)

    # carve out a floor for each room
    for room in rooms:
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                grid[y][x] = "0"

    for i in range(len(rooms) - 1):
        x1, y1 = room_center(rooms[i])
        x2, y2 = room_center(rooms[i + 1])
        carve_corridor(grid, x1, y1, x2, y2)


    # convert each row (a list of characters) into a string
    result = []
    for row in grid:
        result.append("".join(row))
    return result


def room_center(room):
    center_x = room.x + room.width // 2
    center_y = room.y + room.height // 2
    return center_x, center_y


def carve_corridor(grid, x1, y1, x2, y2):
    # horizontal segment first
    x_start = min(x1, x2)
    x_end = max(x1, x2)
    for x in range(x_start, x_end + 1):
        grid[y1][x] = "0"

    # then vertical segment
    y_start = min(y1, y2)
    y_end = max(y1, y2)
    for y in range(y_start, y_end + 1):
        grid[y][x2] = "0"


#testing 

#testing

whole_map = Rect(0, 0, 40, 20)
pieces = split_recursive(whole_map, 3)
actual_rooms = []
for piece in pieces:
    actual_rooms.append(rect_to_room(piece))

generated_map = rooms_to_map(actual_rooms, 40, 20)
for row in generated_map:
    print(row)

    
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

            # enemy takes its turn right after the player moves/attacks
            if enemy_alive:
                dx = player_x - enemy_x
                dy = player_y - enemy_y
                if abs(dx) + abs(dy) == 1:
                    player_hp -= 2
                    if player_hp <= 0:
                        game_over = True
                else:
                    if abs(dx) > abs(dy):
                        step = 1 if dx > 0 else -1
                        if not is_wall(enemy_x + step, enemy_y):
                            enemy_x += step
                    elif dy != 0:
                        step = 1 if dy > 0 else -1
                        if not is_wall(enemy_x, enemy_y + step):
                            enemy_y += step

    screen.fill((30, 30, 40))
    for grid_y, row in enumerate(LEVEL_MAP):  
        for grid_x, cell in enumerate(row):
            if cell == "1":
                color = (60, 60, 70)
            else:
                color = (35, 35, 45)

            pygame.draw.rect(screen, color, (TILE_SIZE * grid_x, TILE_SIZE * grid_y, TILE_SIZE, TILE_SIZE))

    pygame.draw.rect(screen, (80, 200, 255), (TILE_SIZE * player_x,TILE_SIZE * player_y , TILE_SIZE, TILE_SIZE))
    if enemy_alive:
        pygame.draw.rect(screen, (220, 60, 60), (TILE_SIZE * enemy_x, TILE_SIZE * enemy_y, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()