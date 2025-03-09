import pygame
import math
import random
from config import TILE_SIZE, RED, YELLOW

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, name, hp, attack, exp_reward):
        super().__init__()
        # Load enemy sprite instead of using a colored square
        try:
            idle_sheet = pygame.image.load('assets/orcs_idle.png').convert_alpha()
            self.idle_sprites = self.extract_sprites(idle_sheet, 8)
            self.image = self.idle_sprites[0]  # Set initial sprite
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except (pygame.error, AttributeError):
            # Fallback if image loading fails or extract_sprites doesn't exist
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.name = name
        self.max_hp = hp
        self.hp = self.max_hp
        self.attack = attack
        self.exp_reward = exp_reward
        self.aggro_range = 150
        
        # Add variables for health bar display
        self.health_bar_width = TILE_SIZE
        self.health_bar_height = 5
        self.show_damage = False
        self.damage_timer = 0
        self.damage_amount = 0
        
        # Add speed attribute
        self.speed = random.randint(1, 10)  # Example speed value, adjust as needed
        
    def extract_sprites(self, sheet, frames):
        # Extract individual frames from a sprite sheet
        # Assuming horizontal sprite sheet with equal-sized frames
        sprites = []
        width = sheet.get_width() // frames
        height = sheet.get_height()
        
        for i in range(frames):
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sheet, (0, 0), rect)
            sprites.append(surface)
        
        return sprites
        
    def update(self, player):
        # Simple AI: Move toward player if in aggro range
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < self.aggro_range:
            # Normalize direction and move
            if dist > 0:
                dx /= dist
                dy /= dist
                
            self.rect.x += dx
            self.rect.y += dy
            
        # Update damage display timer if showing damage
        if self.show_damage:
            self.damage_timer -= 1
            if self.damage_timer <= 0:
                self.show_damage = False
                
    def draw_health_bar(self, surface, camera=None):
        # Calculate position above the enemy
        bar_x = self.rect.x
        bar_y = self.rect.y - 10
        
        if camera:
            bar_x, bar_y = camera.apply_point(bar_x, bar_y)
        
        # Draw background
        pygame.draw.rect(surface, (0, 0, 0), 
                         (bar_x, bar_y, self.health_bar_width, self.health_bar_height))
        
        # Calculate health ratio
        health_ratio = self.hp / self.max_hp
        fill_width = int(self.health_bar_width * health_ratio)
        
        # Draw filled portion
        pygame.draw.rect(surface, (255, 0, 0), 
                         (bar_x, bar_y, fill_width, self.health_bar_height))
        
        # Draw damage text if needed
        if self.show_damage:
            font = pygame.font.Font(None, 20)
            damage_text = font.render(f"-{self.damage_amount}", True, (255, 0, 0))
            text_x = bar_x + self.health_bar_width // 2 - damage_text.get_width() // 2
            text_y = bar_y - 15
            surface.blit(damage_text, (text_x, text_y))
    
    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        # Show damage amount above enemy
        self.show_damage = True
        self.damage_timer = 60  # Show for 60 frames (1 second at 60 FPS)
        self.damage_amount = amount
        return self.hp <= 0

class GrandMaster(Enemy):
    def __init__(self, x, y, name, hp, attack, exp_reward, skills):
        super().__init__(x, y, name, hp, attack, exp_reward)
        try:
            boss_image = pygame.image.load('assets/orcs_idle.png').convert_alpha()
            self.image = pygame.transform.scale(boss_image, (TILE_SIZE * 1.5, TILE_SIZE * 1.5))
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE * 1.5, TILE_SIZE * 1.5))
            self.image.fill(YELLOW)  # Different color for bosses
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.skills = skills
        self.current_phase = 1
        self.phase_threshold = self.max_hp // 2
        self.health_bar_width = TILE_SIZE * 1.5
        
    def use_skill(self):
        if self.hp < self.phase_threshold and self.current_phase == 1:
            self.current_phase = 2
            return {"name": "Phase Change", "damage": 0, "effect": "The Grandmaster enters phase 2!"}
            
        skill = random.choice(self.skills)
        return skill