import pygame
from config import WHITE, BLACK

class Camera:
    def __init__(self, width, height, screen_width, screen_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x_offset = 0
        self.y_offset = 0
        
    def apply(self, entity):
        """Return the screen position for an entity."""
        return entity.rect.move(self.x_offset, self.y_offset)
        
    def apply_rect(self, rect):
        """Return the screen position for a rect."""
        return rect.move(self.x_offset, self.y_offset)
        
    def apply_point(self, x, y):
        """Return the screen position for a point."""
        return (x + self.x_offset, y + self.y_offset)
        
    def update(self, target):
        """Update camera position to follow target."""
        # Calculate where camera should be
        x = -target.rect.centerx + self.screen_width // 2
        y = -target.rect.centery + self.screen_height // 2
        
        # Limit scrolling to map edges
        x = min(0, x)  # Left edge
        y = min(0, y)  # Top edge
        x = max(-(self.width - self.screen_width), x)  # Right edge
        y = max(-(self.height - self.screen_height), y)  # Bottom edge
        
        # Update offsets
        self.x_offset = int(x)
        self.y_offset = int(y)

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)
        
    def clear_screen(self):
        self.screen.fill(WHITE)
        
    def draw_sprite(self, sprite, camera=None):
        """Draw a sprite with camera offset if provided."""
        if not hasattr(sprite, 'image') or not hasattr(sprite, 'rect'):
            return
            
        if camera:
            # Get screen position
            screen_rect = camera.apply(sprite)
            self.screen.blit(sprite.image, screen_rect)
        else:
            self.screen.blit(sprite.image, sprite.rect)
    
    def draw_sprite_group(self, sprite_group, camera=None):
        """Draw a group of sprites with camera offset if provided."""
        for sprite in sprite_group:
            self.draw_sprite(sprite, camera)
            
            # Draw health bars for entities that have them
            if hasattr(sprite, 'draw_health_bar'):
                if camera:
                    # Get screen position for health bar
                    screen_rect = camera.apply(sprite)
                    sprite.draw_health_bar(self.screen, screen_rect.x, screen_rect.y)
                else:
                    sprite.draw_health_bar(self.screen, sprite.rect.x, sprite.rect.y)
        
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