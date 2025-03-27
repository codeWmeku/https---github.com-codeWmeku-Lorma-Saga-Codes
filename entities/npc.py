import pygame
import os

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, name, dialogue_lines):
        super().__init__()
        
        # Create a colored rectangle as placeholder sprite
        SCALE = 2.0
        SIZE = (32 * SCALE, 32 * SCALE)
        self.image = pygame.Surface(SIZE)
        self.image.fill((0, 255, 255))  # Cyan for NPCs
        # Add a border
        pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Create interaction area around NPC
        self.interaction_rect = self.rect.inflate(20, 20)
        
        # NPC properties
        self.name = name
        self.dialogue_lines = dialogue_lines
        self.current_line = 0
        
        # Interaction indicator
        self.show_indicator = False
        self.indicator_image = self._create_indicator()
        self.indicator_offset = -20  # Pixels above NPC
    
    def _create_indicator(self):
        """Create an interaction indicator (e.g., '!' symbol)"""
        surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(surface, (255, 255, 0), 
            [(10, 0), (20, 20), (0, 20)], 0)  # Triangle
        return surface
    
    def update(self):
        # Update interaction indicator position
        self.interaction_rect.center = self.rect.center
    
    def get_next_dialogue(self):
        """Get the next line of dialogue and cycle through them."""
        if not self.dialogue_lines:
            return ""
        
        line = self.dialogue_lines[self.current_line]
        self.current_line = (self.current_line + 1) % len(self.dialogue_lines)
        return f"{self.name}: {line}"
    
    def draw_interaction_indicator(self, surface):
        """Draw the interaction indicator when player is nearby."""
        if self.show_indicator:
            indicator_pos = (
                self.rect.centerx - self.indicator_image.get_width() // 2,
                self.rect.top + self.indicator_offset
            )
            surface.blit(self.indicator_image, indicator_pos)