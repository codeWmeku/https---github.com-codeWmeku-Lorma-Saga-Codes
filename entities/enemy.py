import pygame
import math
import random
from config import TILE_SIZE, RED, YELLOW

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, name="Enemy", hp=50, attack=10, exp=100):
        super().__init__()
        
        # Create a colored rectangle as placeholder sprite
        SCALE = 2.0
        SIZE = (32 * SCALE, 32 * SCALE)
        self.image = pygame.Surface(SIZE)
        self.image.fill(RED)  # Use RED from config
        # Add a border
        pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 5)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Enemy properties
        self.name = name
        self.max_health = hp
        self.health = hp
        self.attack = attack
        self.exp = exp
        
        # Movement properties
        self.speed = 1
        self.move_timer = 0
        self.move_delay = 2000  # Milliseconds between movement
        self.move_duration = 1000  # Milliseconds to move
        self.moving = False
        self.move_direction = [0, 0]
    
    def update(self):
        """Update enemy state and movement."""
        current_time = pygame.time.get_ticks()
        
        # Check if it's time to start/stop moving
        if not self.moving and current_time - self.move_timer > self.move_delay:
            # Start new movement
            self.move_timer = current_time
            self.moving = True
            # Choose random direction
            self.move_direction = [
                random.choice([-1, 0, 1]),
                random.choice([-1, 0, 1])
            ]
        elif self.moving and current_time - self.move_timer > self.move_duration:
            # Stop movement
            self.moving = False
            self.move_timer = current_time
            self.move_direction = [0, 0]
        
        # Apply movement
        if self.moving:
            self.rect.x += self.move_direction[0] * self.speed
            self.rect.y += self.move_direction[1] * self.speed
            
            # Keep enemy within map bounds (assuming MAP_WIDTH and MAP_HEIGHT)
            self.rect.clamp_ip(pygame.Rect(0, 0, 2000, 2000))  # Using default map size
    
    def take_damage(self, damage):
        """
        Reduce enemy health and return True if defeated.
        
        Args:
            damage (int): Amount of damage to deal
        
        Returns:
            bool: True if enemy is defeated, False otherwise
        """
        self.health = max(0, self.health - damage)
        return self.health <= 0
    
    def draw_health_bar(self, screen):
        """
        Draw a health bar for the enemy.
        
        Args:
            screen (pygame.Surface): Surface to draw health bar on
        """
        bar_width = self.rect.width
        bar_height = 10
        
        # Background of health bar (dark red)
        pygame.draw.rect(screen, (100, 0, 0), 
                         (self.rect.x, self.rect.y - bar_height - 5, 
                          bar_width, bar_height))
        
        # Current health (bright green)
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, (0, 255, 0), 
                         (self.rect.x, self.rect.y - bar_height - 5, 
                          health_width, bar_height))

class GrandMaster(Enemy):
    def __init__(self, x, y, name, hp, attack, exp, skills):
        super().__init__(x, y, name, hp, attack, exp)
        try:
            self.image = pygame.image.load('assets/Characters(100x100)/Orc/Orc with shadows/Orc.png').convert_alpha()
           
        except pygame.error:
            self.image = pygame.Surface((self.rect.width * 1.5, self.rect.height * 1.5))
            self.image.fill(YELLOW)  # Different color for bosses
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.skills = skills
        self.current_phase = 1
        self.phase_threshold = self.max_health // 2
    
    def use_skill(self):
        """Use a random skill from the skill list."""
        if not self.skills:
            return {"name": "Basic Attack", "damage": self.attack}
        
        # More likely to use powerful skills in phase 2
        if self.health < self.phase_threshold and random.random() < 0.7:
            skill = max(self.skills, key=lambda s: s["damage"])
        else:
            skill = random.choice(self.skills)
        
        return skill

def spawn_enemies():
    """Create a group of enemies with predefined positions."""
    enemies = pygame.sprite.Group()
    
    # Predefined enemy locations based on map coordinates
    enemy_positions = [
        (50 * TILE_SIZE, 250 * TILE_SIZE, "Orc Warrior", 50, 10, 25),
        (100 * TILE_SIZE, 450 * TILE_SIZE, "Orc Warrior", 40, 8, 20),
        (500 * TILE_SIZE, 500 * TILE_SIZE, "Orc Warrior", 60, 12, 30),
        (100 * TILE_SIZE, 50 * TILE_SIZE, "Orc Warrior", 60, 12, 30),
        (450 * TILE_SIZE, 500 * TILE_SIZE, "Orc Warrior", 60, 12, 30)
    ]
    
    for x, y, name, hp, attack, exp in enemy_positions:
        enemy = Enemy(x, y, name, hp, attack, exp)
        enemies.add(enemy)
    
    return enemies