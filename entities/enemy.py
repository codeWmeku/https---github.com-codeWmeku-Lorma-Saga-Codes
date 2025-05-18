import pygame
import math
import random
import os
from config import TILE_SIZE, RED, YELLOW

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, name="Enemy", hp=50, attack=10, exp=100):
        super().__init__()
        
        # Enemy properties first so they can be used by sprite methods
        self.name = name
        self.max_health = hp
        self.health = hp
        self.attack = attack
        self.exp = exp
        
        # Sprite dimensions
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Pulse animation variables
        self.pulse_timer = 0
        self.pulse_direction = 1
        self.pulse_amount = 0
        
        # Animation variables
        self.frame = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()
        
        # Create custom Mzana-like appearance but smaller
        self.create_mzana_like_sprite()
        
        # Movement properties
        self.speed = 1
        self.move_timer = 0
        self.move_delay = 2000  # Milliseconds between movement
        self.move_duration = 1000  # Milliseconds to move
        self.moving = False
        self.move_direction = [0, 0]
    
    def create_mzana_like_sprite(self):
        """Create a smaller version of the Mzana boss sprite with varied colors."""
        # Create a transparent surface
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Enhanced color selection with more variety and vibrant colors
        enemy_types = {
            "Skeleton": {
                "main": (200, 200, 200),  # Light gray
                "accent": (150, 150, 150),  # Darker gray
                "eye": (255, 0, 0)         # Red eyes
            },
            "Ghost": {
                "main": (150, 150, 255),    # Light blue
                "accent": (100, 100, 200),  # Darker blue
                "eye": (255, 255, 255)      # White eyes
            },
            "Goblin": {
                "main": (100, 200, 100),    # Green
                "accent": (50, 150, 50),    # Darker green
                "eye": (255, 255, 0)        # Yellow eyes
            },
            "Wraith": {
                "main": (80, 0, 80),        # Dark purple
                "accent": (120, 0, 120),    # Brighter purple
                "eye": (255, 100, 255)      # Pink eyes
            },
            "Elemental": {
                "main": (255, 100, 0),      # Orange
                "accent": (255, 50, 0),     # Red-orange
                "eye": (255, 255, 0)        # Yellow eyes
            },
            "Slime": {
                "main": (0, 255, 100),      # Lime green
                "accent": (0, 200, 80),     # Darker lime
                "eye": (0, 0, 0)            # Black eyes
            },
            "Undead": {
                "main": (100, 255, 255),    # Cyan
                "accent": (0, 200, 200),    # Darker cyan
                "eye": (255, 0, 0)          # Red eyes
            },
            "Demon": {
                "main": (255, 0, 0),        # Red
                "accent": (200, 0, 0),      # Dark red
                "eye": (255, 255, 0)        # Yellow eyes
            },
            "Fairy": {
                "main": (255, 150, 255),    # Pink
                "accent": (200, 100, 200),  # Darker pink
                "eye": (0, 255, 255)        # Cyan eyes
            },
            "Corrupted": {
                "main": (0, 0, 0),          # Black
                "accent": (50, 50, 50),     # Dark gray
                "eye": (255, 0, 0)          # Red eyes
            },
            # New vibrant colors as requested
            "Sapphire": {
                "main": (0, 50, 255),       # Deep blue
                "accent": (0, 100, 200),    # Medium blue
                "eye": (255, 255, 255)      # White eyes
            },
            "Solar": {
                "main": (255, 255, 0),      # Bright yellow
                "accent": (255, 200, 0),    # Gold
                "eye": (255, 100, 0)        # Orange eyes
            },
            "Aquamarine": {
                "main": (0, 255, 255),      # Bright cyan
                "accent": (0, 200, 255),    # Turquoise
                "eye": (0, 0, 255)          # Blue eyes
            },
            "Royal": {
                "main": (100, 0, 255),      # Royal purple
                "accent": (75, 0, 200),     # Deep purple
                "eye": (255, 255, 0)        # Gold eyes
            },
            "Emerald": {
                "main": (0, 200, 50),       # Emerald green
                "accent": (0, 150, 50),     # Darker emerald
                "eye": (255, 255, 255)      # White eyes
            },
            "Amber": {
                "main": (255, 191, 0),      # Amber
                "accent": (255, 170, 0),    # Darker amber
                "eye": (0, 0, 0)            # Black eyes
            },
            "Scarlet": {
                "main": (255, 36, 0),       # Scarlet red
                "accent": (200, 30, 0),     # Darker scarlet
                "eye": (255, 255, 200)      # Light yellow eyes
            },
            "Teal": {
                "main": (0, 128, 128),      # Teal
                "accent": (0, 100, 100),    # Darker teal
                "eye": (200, 255, 255)      # Light cyan eyes
            }
        }
        
        # If the enemy has a recognized type, use its colors
        # Otherwise randomly select one of the color schemes
        if self.name in enemy_types:
            color_scheme = enemy_types[self.name]
        else:
            # Pick a random enemy type
            random_type = random.choice(list(enemy_types.keys()))
            color_scheme = enemy_types[random_type]
            # Set the enemy name to match the colors
            self.name = random_type
            
        main_color = color_scheme["main"]
        accent_color = color_scheme["accent"]
        eye_color = color_scheme["eye"]
        
        # Add some random variation to the colors to make enemies more unique
        # Shift hue slightly for more individuality
        main_color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in main_color)
        accent_color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in accent_color)
            
        # Draw a Mzana-like shape but smaller
        pygame.draw.circle(self.image, main_color, (self.width//2, self.height//2), self.width//2-5)
        
        # Draw details to make it look like Mzana
        # Eyes
        eye_radius = self.width // 10
        eye_offset = self.width // 5
        pygame.draw.circle(self.image, eye_color, (self.width//2 - eye_offset, self.height//2 - eye_offset), eye_radius)
        pygame.draw.circle(self.image, eye_color, (self.width//2 + eye_offset, self.height//2 - eye_offset), eye_radius)
        
        # Mouth
        mouth_rect = pygame.Rect(self.width//2 - self.width//5, self.height//2 + self.height//8, 
                              self.width//2.5, self.height//8)
        pygame.draw.ellipse(self.image, accent_color, mouth_rect)
        
        # Decorative patterns - more complex patterns based on enemy type
        if "Elemental" in self.name or "Fairy" in self.name:
            # Add glowing aura effect
            for r in range(3):
                glow_radius = self.width//2 - 5 - r*2
                glow_color = tuple(max(0, min(255, c + 50)) for c in main_color) + (150 - r*50,)  # Add alpha
                glow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, glow_color, (self.width//2, self.height//2), glow_radius)
                self.image.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        else:
            # Standard decorative patterns
            pattern_radius = self.width // 12
            pattern_count = random.randint(4, 7)  # Vary the number of patterns
            for i in range(pattern_count):
                angle = i * (2 * math.pi / pattern_count)
                x = self.width//2 + int(math.cos(angle) * (self.width//2 - 10))
                y = self.height//2 + int(math.sin(angle) * (self.height//2 - 10))
                pygame.draw.circle(self.image, accent_color, (x, y), pattern_radius)
        
        # Add name text
        font = pygame.font.Font(None, 12)
        name_text = font.render(self.name, True, (255, 255, 255))
        self.image.blit(name_text, (self.width//2 - name_text.get_width()//2, self.height - 10))
        
    def update(self):
        """Update enemy state, animation and movement."""
        current_time = pygame.time.get_ticks()
        
        # Update pulsing animation
        self.pulse_timer += 0.1
        self.pulse_amount = math.sin(self.pulse_timer) * 2
        
        # Recreate the sprite with the current pulse to animate it
        self.create_animated_sprite()
        
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
            
            # Keep enemy within map bounds
            self.rect.clamp_ip(pygame.Rect(0, 0, 2000, 2000))
            
    def create_animated_sprite(self):
        """Create an animated version of the Mzana-like sprite with pulsing effect."""
        # Create a new surface for the animated sprite
        animated_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        animated_image.fill((0, 0, 0, 0))  # Transparent base
        
        # Determine color scheme based on enemy type
        if "Knight" in self.name:
            main_color = (120, 0, 180)  # Purple
            head_color = (80, 0, 120)
            detail_color = (40, 0, 80)
        elif "Wizard" in self.name:
            main_color = (0, 80, 180)  # Blue
            head_color = (0, 40, 120)
            detail_color = (0, 20, 80)
        elif "Skeletal" in self.name:
            main_color = (100, 100, 100)  # Gray
            head_color = (60, 60, 60)
            detail_color = (30, 30, 30)
        else:
            main_color = (180, 0, 0)    # Red like Mzana
            head_color = (120, 0, 0)
            detail_color = (80, 0, 0)
            
        # Calculate pulsing size
        body_size = int(self.width//2 - 5 + self.pulse_amount)
        head_size = int(self.width//5 + self.pulse_amount/2)
        
        # Draw the pulsing sprite elements
        # Main body
        pygame.draw.circle(animated_image, main_color, (self.width//2, self.height//2), body_size)
        # Head
        pygame.draw.circle(animated_image, head_color, (self.width//2, self.height//3), head_size)
        # Eyes
        eye_size = 2 + abs(self.pulse_amount/4)
        pygame.draw.circle(animated_image, (255, 255, 0), (self.width//2 - 8, self.height//3), eye_size)
        pygame.draw.circle(animated_image, (255, 255, 0), (self.width//2 + 8, self.height//3), eye_size)
        # Details
        pygame.draw.rect(animated_image, detail_color, (self.width//4, 2*self.height//3, self.width//2, self.height//8))
        
        # Add name text
        font = pygame.font.Font(None, 12)
        name_text = font.render(self.name, True, (255, 255, 255))
        animated_image.blit(name_text, (self.width//2 - name_text.get_width()//2, self.height - 10))
        
        # Update the image
        self.image = animated_image
    
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
        
        # Make the boss visually distinct
        self.image.fill(YELLOW)  # Use yellow color for bosses
        
        # Boss-specific attributes
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
        # Create enemy with parameters in the right order
        enemy = Enemy(x, y, name, hp, attack, exp)
        enemies.add(enemy)
    
    return enemies