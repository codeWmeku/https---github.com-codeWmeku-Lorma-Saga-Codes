import pygame
from config import BLACK

class Button:
    def __init__(self, x, y, width, height, text, color, highlight_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.highlight_color = highlight_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.highlight_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def update(self):
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        
    def is_clicked(self):
        return self.is_hovered and pygame.mouse.get_pressed()[0]