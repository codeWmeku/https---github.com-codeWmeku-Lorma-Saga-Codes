import pygame
from config import TILE_SIZE, GREEN

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, name, dialogue):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.name = name
        self.dialogue = dialogue
        self.interaction_range = 50