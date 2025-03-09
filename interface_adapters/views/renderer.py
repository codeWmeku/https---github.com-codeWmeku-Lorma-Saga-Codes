import pygame
from config import WHITE, BLACK

class Camera:
    def __init__(self, width, height, screen_width, screen_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
        
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
        
    def apply_point(self, x, y):
        return x + self.camera.x, y + self.camera.y
        
    def update(self, target):
        x = -target.rect.x + self.screen_width // 2
        y = -target.rect.y + self.screen_height // 2
        
        # Limit scrolling to map size
        x = min(0, x)  # Left
        y = min(0, y)  # Top
        x = max(-(self.width - self.screen_width), x)  # Right
        y = max(-(self.height - self.screen_height), y)  # Bottom
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)
        
    def clear_screen(self):
        self.screen.fill(WHITE)
        
    def draw_sprite(self, sprite, camera=None):
        if hasattr(sprite, 'draw'):
            # Use custom draw method if available
            sprite.draw(self.screen, camera)
        else:
            # Default sprite drawing
            if camera:
                self.screen.blit(sprite.image, camera.apply(sprite))
            else:
                self.screen.blit(sprite.image, sprite.rect)
                
    def draw_sprite_group(self, sprite_group, camera=None):
        for sprite in sprite_group:
            self.draw_sprite(sprite, camera)
            # Draw health bars above enemies
            if hasattr(sprite, 'draw_health_bar'):
                sprite.draw_health_bar(self.screen, camera)
        
    def draw_text(self, text, x, y, color=BLACK):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
        
    def draw_health_bar(self, x, y, width, height, value, max_value, color):
        # Draw background
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height))
        
        # Calculate fill width
        fill_width = (value / max_value) * width if max_value > 0 else 0
        
        # Draw fill
        pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        
        # Draw border
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height), 1)