import pygame
from game_map import GameMap
from player import Player
from orc import Orc

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Lorma Saga")

# Clock for FPS
clock = pygame.time.Clock()

# Load game map
game_map = GameMap(SCREEN_WIDTH, SCREEN_HEIGHT)

# Load player
player = Player()

# Load Orcs (enemies)
orcs = [Orc(400, 300), Orc(600, 400), Orc(700, 200)]  # Add more orcs if needed

# Group for drawing
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(*orcs)

# Camera position
camera_x, camera_y = 0, 0

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen
    keys = pygame.key.get_pressed()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move player
    player.handle_movement(keys)
    player.update_animation()
    player.update_projectiles(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Camera follows player
    camera_x = player.x - SCREEN_WIDTH // 2
    camera_y = player.y - SCREEN_HEIGHT // 2
    camera_x = max(0, camera_x)
    camera_y = max(0, camera_y)

    # Draw background (Replace with game_map later)
    screen.fill((0, 255, 0))  

    # Draw map
    game_map.draw(screen, camera_x, camera_y)

    # Update Orcs
    for orc in orcs:
        orc.update(player)

    # Draw Player & Orcs
    all_sprites.update()
    player.draw(screen)
    for orc in orcs:
        orc.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()
