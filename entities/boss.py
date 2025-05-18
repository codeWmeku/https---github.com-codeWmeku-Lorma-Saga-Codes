import pygame
import os
import random

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, name="Mzana", health=500, attack=25, exp=100):
        super().__init__()
        
        # Basic properties
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp = exp
        self.speed = 1
        self.is_boss = True
        
        # Position and size properties
        self.x = x
        self.y = y
        self.width = 100
        self.height = 100
        
        # Load sprite
        self.load_boss_sprite()
        
        # Create rect for collisions
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # State tracking
        self.is_defeated = False
        
    def load_boss_sprite(self):
        """Load the boss sprite image"""
        try:
            # Load the idle animation for a better-looking boss
            img_path = os.path.join('assets', 'boss', 'NightBorne_idle.gif')
            if os.path.exists(img_path):
                print(f"Loading boss idle animation: {img_path}")
                # Use a static frame from the animation for simplicity
                # We'll create a proper red and black boss appearance
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self.image.fill((0, 0, 0, 0))  # Transparent base
                
                # Draw a more intimidating boss shape
                # Main body
                pygame.draw.circle(self.image, (180, 0, 0), (self.width//2, self.height//2), self.width//2-10)
                # Head
                pygame.draw.circle(self.image, (120, 0, 0), (self.width//2, self.height//3), self.width//4)
                # Eyes
                pygame.draw.circle(self.image, (255, 255, 0), (self.width//2 - 12, self.height//3), 5)
                pygame.draw.circle(self.image, (255, 255, 0), (self.width//2 + 12, self.height//3), 5)
                # Details
                pygame.draw.rect(self.image, (80, 0, 0), (self.width//4, 2*self.height//3, self.width//2, self.height//6))
                
                # Add some text to identify as Mzana
                font = pygame.font.Font(None, 20)
                name_text = font.render("MZANA", True, (255, 255, 255))
                self.image.blit(name_text, (self.width//2 - name_text.get_width()//2, self.height - 20))
            else:
                # Fallback to a colored rectangle if file doesn't exist
                print(f"Boss animation file not found: {img_path}")
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill((200, 0, 0))  # Red for the boss
        except Exception as e:
            print(f"Error loading boss image: {e}")
            # Create a fallback colored rectangle
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 0, 0))  # Red for the boss
    
    def update(self):
        """Update boss state"""
        # If we add animations or movement later, implement it here
        pass
    
    def take_damage(self, damage):
        """Reduce health when taking damage"""
        self.health = max(0, self.health - damage)
        is_defeated = self.health <= 0
        if is_defeated:
            self.is_defeated = True
        return is_defeated
    
    def draw_health_bar(self, screen, x, y):
        """Draw a health bar for the boss"""
        bar_width = 100
        bar_height = 10
        bar_x = x + (self.width - bar_width) // 2
        bar_y = y - 20  # Position above the boss
        
        # Draw background
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Calculate current health width
        health_width = int((self.health / self.max_health) * bar_width)
        
        # Draw current health
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Draw boss name above health bar
        font = pygame.font.Font(None, 24)
        name_text = font.render(self.name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(bar_x + bar_width // 2, bar_y - 15))
        screen.blit(name_text, name_rect)
