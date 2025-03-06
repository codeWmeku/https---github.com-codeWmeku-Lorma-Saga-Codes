import pygame

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background = pygame.image.load("assets/grass.png").convert()
        self.tree = pygame.image.load("assets/tree.png").convert_alpha()

    def draw(self, screen, camera_x, camera_y):
        """Draw the map and obstacles."""
        screen.blit(self.background, (-camera_x, -camera_y))
        screen.blit(self.tree, (300 - camera_x, 200 - camera_y))
        screen.blit(self.tree, (500 - camera_x, 350 - camera_y))
