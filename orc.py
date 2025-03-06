import pygame

class Orc(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/orcs_walk.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2

    def update(self, player):
        """Move toward the player."""
        if player.x > self.rect.x:
            self.rect.x += self.speed
        elif player.x < self.rect.x:
            self.rect.x -= self.speed

        if player.y > self.rect.y:
            self.rect.y += self.speed
        elif player.y < self.rect.y:
            self.rect.y -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
