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

class PauseMenu:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.buttons = [
            Button(screen_width//2 - 100, screen_height//2 - 50, 200, 50, "Resume", (100, 200, 100), (150, 255, 150)),
            Button(screen_width//2 - 100, screen_height//2 + 10, 200, 50, "Main Menu", (200, 100, 100), (255, 150, 150))
        ]
        
    def draw(self, screen):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        font = pygame.font.Font(None, 48)
        text_surface = font.render("PAUSED", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width//2, self.height//2 - 150))
        screen.blit(text_surface, text_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
            button.update()
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.is_clicked():
                        if button.text == "Resume":
                            return "resume"
                        elif button.text == "Main Menu":
                            return "main_menu"
        return None