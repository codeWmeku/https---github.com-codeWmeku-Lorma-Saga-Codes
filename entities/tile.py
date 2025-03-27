import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, is_wall=False):
        super().__init__()
        
        # Store the image and position
        self.image = image
        self.rect = pygame.Rect(x, y, 0, 0) if image is None else image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Collision properties
        self.is_wall = is_wall
        if is_wall and image:
            # Create a smaller collision rect for walls
            self.collision_rect = pygame.Rect(0, 0, self.rect.width * 0.8, self.rect.height * 0.8)
            self.collision_rect.centerx = self.rect.centerx
            self.collision_rect.centery = self.rect.centery
        else:
            self.collision_rect = self.rect
