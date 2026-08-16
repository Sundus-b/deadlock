import pygame
pygame.init()


screen = pygame.display.set_mode((640, 480))

clock = pygame.time.Clock()
running = True

TILE_SIZE = 32
player_x = 3  #3 tiles over , 3 tiles down
player_y = 3

enemy_x = 7
enemy_y = 3
enemy_hp = 10

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

    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                new_x = player_x + 1
                new_y = player_y
                if not is_wall(new_x, new_y):
                    player_x = new_x

            elif event.key == pygame.K_LEFT:
                new_x = player_x - 1
                new_y = player_y
                if not is_wall(new_x, new_y):
                    player_x = new_x

            elif event.key == pygame.K_UP:
                new_x = player_x
                new_y = player_y - 1
                if not is_wall(new_x, new_y):
                    player_y = new_y

            elif event.key == pygame.K_DOWN:
                new_x = player_x
                new_y = player_y + 1
                if not is_wall(new_x, new_y):
                     player_y = new_y

    screen.fill((30, 30, 40))
    for grid_y, row in enumerate(LEVEL_MAP):  
        for grid_x, cell in enumerate(row):
            if cell == "1":
                color = (60, 60, 70)
            else:
                color = (35, 35, 45)

            pygame.draw.rect(screen, color, (TILE_SIZE * grid_x, TILE_SIZE * grid_y, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, (80, 200, 255), (TILE_SIZE * player_x,TILE_SIZE * player_y , TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, (220, 60, 60), (TILE_SIZE * enemy_x, TILE_SIZE * enemy_y, TILE_SIZE, TILE_SIZE))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()