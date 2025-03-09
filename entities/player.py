import pygame
from config import MAP_HEIGHT, MAP_WIDTH, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, BLUE

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load sprite animations
        self.load_sprites()
        self.current_sprite = 0
        self.image = self.idle_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation state
        self.animation_state = "idle"  # idle, walking, attacking
        self.animation_cooldown = 100  # milliseconds between frames
        self.last_update = pygame.time.get_ticks()
        self.facing_right = True  # Track direction player is facing
        
        # Player stats
        self.name = "Player"
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = 15
        self.skill_damage = 25
        self.speed = 3
        self.level = 1
        self.exp = 0
        self.next_level_exp = 100
        
        # Attack cooldown
        self.attacking = False
        self.attack_cooldown = 500  # milliseconds
        self.last_attack = 0
    
    def load_sprites(self):
        # Load sprite sheets and extract frames
        try:
            # Idle animation
            idle_sheet = pygame.image.load('assets/Idle.png').convert_alpha()
            self.idle_sprites = self.extract_sprites(idle_sheet, 8)  # Assuming 8 frames
            
            # Walking animation
            walk_sheet = pygame.image.load('assets/Walk.png').convert_alpha()
            self.walk_sprites = self.extract_sprites(walk_sheet, 8)  # Assuming 8 frames
            
            # Attack animation
            attack_sheet = pygame.image.load('assets/Attack.png').convert_alpha()
            self.attack_sprites = self.extract_sprites(attack_sheet, 8)  # Assuming 8 frames
        except pygame.error:
            # Fallback if sprites not found
            print("Warning: Could not load sprite sheets. Using placeholder sprites.")
            self.idle_sprites = [self.create_placeholder_sprite()]
            self.walk_sprites = [self.create_placeholder_sprite()]
            self.attack_sprites = [self.create_placeholder_sprite()]
    
    def create_placeholder_sprite(self):
        # Create a placeholder sprite if images can't be loaded
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(BLUE)
        return surface
    
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
    
    def update_animation(self):
        # Update the sprite animation based on current state
        current_time = pygame.time.get_ticks()
        
        # Update animation frame if cooldown has passed
        if current_time - self.last_update >= self.animation_cooldown:
            self.last_update = current_time
            
            # Cycle through appropriate animation frames
            if self.animation_state == "idle":
                self.current_sprite = (self.current_sprite + 1) % len(self.idle_sprites)
                self.image = self.idle_sprites[self.current_sprite]
            elif self.animation_state == "walking":
                self.current_sprite = (self.current_sprite + 1) % len(self.walk_sprites)
                self.image = self.walk_sprites[self.current_sprite]
            elif self.animation_state == "attacking":
                self.current_sprite = (self.current_sprite + 1) % len(self.attack_sprites)
                self.image = self.attack_sprites[self.current_sprite]
                
                # If we've reached the end of the attack animation
                if self.current_sprite == len(self.attack_sprites) - 1:
                    self.animation_state = "idle"
                    self.attacking = False
            
            # Flip sprite if facing left
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
    
    def move(self, dx, dy, walls):
        # Set animation state based on movement
        if dx != 0 or dy != 0:
            self.animation_state = "walking"
            # Update facing direction
            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False
        else:
            # If not moving and not attacking, set to idle
            if self.animation_state != "attacking":
                self.animation_state = "idle"
        
        wall_hit = False
        
        # Move horizontally and check collisions
        if dx != 0:
            self.rect.x += dx * self.speed
            
            # Check for collisions with walls after horizontal movement
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    wall_hit = True
                    if dx > 0:  # Moving right
                        self.rect.right = wall.rect.left
                    else:  # Moving left
                        self.rect.left = wall.rect.right
                    break  # Stop checking after first collision
        
        # Move vertically and check collisions
        if dy != 0:
            self.rect.y += dy * self.speed
            
            # Check for collisions with walls after vertical movement
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    wall_hit = True
                    if dy > 0:  # Moving down
                        self.rect.bottom = wall.rect.top
                    else:  # Moving up
                        self.rect.top = wall.rect.bottom
                    break  # Stop checking after first collision
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
            wall_hit = True
        if self.rect.right > MAP_WIDTH:
            self.rect.right = MAP_WIDTH
            wall_hit = True
        if self.rect.top < 0:
            self.rect.top = 0
            wall_hit = True
        if self.rect.bottom > MAP_HEIGHT:
            self.rect.bottom = MAP_HEIGHT
            wall_hit = True
        
        # Update animation
        self.update_animation()
        
        return wall_hit  # Return whether a collision occurred
        
    def attack_action(self):
        # Initiate attack animation
        current_time = pygame.time.get_ticks()
        if not self.attacking and current_time - self.last_attack >= self.attack_cooldown:
            self.animation_state = "attacking"
            self.current_sprite = 0
            self.attacking = True
            self.last_attack = current_time
            
            # Create attack hitbox in the direction player is facing
            attack_rect = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE)
            if self.facing_right:
                attack_rect.x = self.rect.right
            else:
                attack_rect.x = self.rect.x - TILE_SIZE
                
            return attack_rect
        return pygame.Rect(0, 0, 0, 0)
    
    def level_up(self):
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.attack += 5
        self.skill_damage += 8
        self.next_level_exp = int(self.next_level_exp * 1.5)
        return f"{self.name} leveled up to level {self.level}!"
    
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.next_level_exp:
            return self.level_up()
        return None
    
    def use_skill(self):
        self.attack_action()  # Trigger attack animation for skill use
        return self.skill_damage
    
    def basic_attack(self):
        self.attack_action()  # Trigger attack animation
        return self.attack