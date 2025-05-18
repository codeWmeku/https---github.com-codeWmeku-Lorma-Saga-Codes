import pygame
import os
import logging

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Animation properties
        self.animation_state = "idle"
        self.current_frame = 0
        self.animation_speed = 0.15  # Slower for smoother animation
        self.animation_timer = 0
        self.facing_right = True
        self.last_update_time = pygame.time.get_ticks()
        
        # Load sprites first
        self.load_sprites()
        
        # Position and movement
        self.rect = pygame.Rect(x, y, 150, 150)  # Increased size from 100 to 150
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 3  # Reduced from 5 to 3
        self.max_speed = 5  # Reduced from 7 to 5
        self.acceleration = 0.3  # Slightly reduced acceleration
        self.friction = 0.9  # Increased friction for slower movement
        self.moving = False
        
        # Create a smaller collision rect for more precise collisions
        self.collision_rect = pygame.Rect(0, 0, self.rect.width * 0.6, self.rect.height * 0.3)
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.bottom = self.rect.bottom
        
        # Combat properties
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.is_attacking = False
        self.exp = 0
        self.level = 1
        self.exp_to_next_level = 100  # Always 100 XP per level
        
        # Additional character attributes
        self.defense = 5           # Reduces damage taken
        self.critical_chance = 10  # Percentage chance for critical hits (1.5x damage)
        self.speed = 3             # Affects turn order and dodge chance
        
        # Player ID selection
        self.player_id = 1  # Default player ID
        
        # Skill 3 - Health Regeneration
        self.skill3_cooldown = 0
        self.skill3_cooldown_max = 180  # 3 seconds at 60 FPS
        self.skill3_heal_amount = 30  # Increased healing amount
        
    def load_sprites(self):
        """Load and scale sprite animations."""
        # Sprite scaling factor
        scale_factor = 1.5  # Increased from default

        # Load sprite sheets or create fallback
        try:
            # Idle sprites
            idle_sheet = pygame.image.load(os.path.join('assets', 'Characters(100x100)', 'Soldier', 'Soldier with shadows', 'Soldier.png')).convert_alpha()
            self.idle_sprites = self.extract_sprites(idle_sheet, 6)
            self.idle_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * scale_factor), 
                                                                 int(sprite.get_height() * scale_factor))) 
                                  for sprite in self.idle_sprites]

            # Walk sprites
            walk_sheet = pygame.image.load(os.path.join('assets', 'Characters(100x100)', 'Soldier', 'Soldier with shadows', 'Soldier-Walk.png')).convert_alpha()
            self.walk_sprites = self.extract_sprites(walk_sheet, 8)
            self.walk_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * scale_factor), 
                                                                 int(sprite.get_height() * scale_factor))) 
                                  for sprite in self.walk_sprites]

            # Attack sprites
            attack_sheet = pygame.image.load(os.path.join('assets', 'Characters(100x100)', 'Soldier', 'Soldier with shadows', 'Soldier-Attack01.png')).convert_alpha()
            self.attack_sprites = self.extract_sprites(attack_sheet, 6)
            self.attack_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * scale_factor), 
                                                                   int(sprite.get_height() * scale_factor))) 
                                    for sprite in self.attack_sprites]

        except Exception as e:
            self.logger.error(f"Error loading player sprites: {e}")
            self.logger.info("Using fallback rectangles.")
            # Create colored rectangles as fallback
            self.idle_sprites = self._create_fallback_frames((255, 0, 0), 4)
            self.walk_sprites = self._create_fallback_frames((0, 255, 0), 6)
            self.attack_sprites = self._create_fallback_frames((0, 0, 255), 4)
            self.idle_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * scale_factor), 
                                                                 int(sprite.get_height() * scale_factor))) 
                                  for sprite in self.idle_sprites]
            self.walk_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * scale_factor), 
                                                                 int(sprite.get_height() * scale_factor))) 
                                  for sprite in self.walk_sprites]
            self.attack_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * scale_factor), 
                                                                   int(sprite.get_height() * scale_factor))) 
                                    for sprite in self.attack_sprites]
        # Set initial sprite
        self.image = self.idle_sprites[0]
    
    def extract_sprites(self, sheet, frame_count):
        """Extract individual sprites from a sprite sheet."""
        sprites = []
        width = sheet.get_width() // frame_count
        height = sheet.get_height()
        
        for i in range(frame_count):
            # Create surface with per-pixel alpha
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            # Copy the sprite from the sheet
            sprite.blit(sheet, (0, 0), (i * width, 0, width, height))
            sprites.append(sprite)
        
        return sprites
    
    def _create_fallback_frames(self, color, count):
        """Create simple colored rectangles as fallback sprites."""
        frames = []
        size = (100, 100)  # Match original sprite size
        for _ in range(count):
            surface = pygame.Surface(size, pygame.SRCALPHA)
            surface.fill(color)
            frames.append(surface)
        return frames
    
    def use_skill3(self):
        """Regenerate health when skill 3 is used."""
        if self.skill3_cooldown <= 0:
            # Calculate healing amount
            heal_amount = self.skill3_heal_amount
            
            # Apply healing (ensure it doesn't exceed max health)
            old_health = self.health
            self.health = min(self.max_health, self.health + heal_amount)
            actual_heal = self.health - old_health
            
            # Set cooldown
            self.skill3_cooldown = self.skill3_cooldown_max
            
            print(f"Healed for {actual_heal} HP. Health: {self.health}/{self.max_health}")
            return True
        
        print(f"Healing on cooldown: {self.skill3_cooldown//60 + 1}s remaining")
        return False
    
    def gain_exp(self, amount):
        """Add experience points and level up if necessary.
        
        Args:
            amount (int): Amount of XP to add
        
        Returns:
            bool: True if leveled up, False otherwise
        """
        # Make sure exp_to_next_level exists
        if not hasattr(self, 'exp_to_next_level'):
            self.exp_to_next_level = 100
            
        self.exp += amount
        leveled = False
        
        # Check if we've accumulated enough XP to level up
        if self.exp >= self.exp_to_next_level:
            # Store excess XP beyond what was needed for this level
            excess_exp = self.exp - self.exp_to_next_level
            
            # Level up and keep excess XP for progress towards next level
            leveled = True
            self.level_up()
            self.exp = excess_exp
            
        return leveled
    
    def set_player_id(self, player_id):
        """Set player ID.
        
        Args:
            player_id (int): The selected player ID (1-5)
        """
        self.player_id = player_id
        
        # Reset stats for new player
        self.health = self.max_health
        self.exp = 0
        self.level = 1
        self.exp_to_next_level = 100
        
        # Print selected player info
        print(f"Selected Player {player_id}")
        
    def level_up(self):
        """Increase player level and scale up stats.
        
        Returns:
            bool: True if successful
        """
        self.level += 1
        
        # Increase max health by 20 per level
        self.max_health += 20
        self.health = self.max_health  # Fully heal on level up
        
        # Scale attack power with level (10% increase per level)
        self.attack_power = round(self.attack_power * 1.1)
        
        # Scale healing with level (10% increase per level)
        self.skill3_heal_amount = round(self.skill3_heal_amount * 1.1)
        
        # Increase XP required for next level (30% more per level)
        self.exp_to_next_level = round(100 * (1.3 ** (self.level - 1)))
        
        level_up_message = f"Level up! Player {self.player_id} is now level {self.level}!"
        stats_message = f"Attack: {self.attack_power}, Defense: {self.defense}, Health: {self.health}/{self.max_health}"
        
        print(level_up_message)
        print(stats_message)
        print(f"XP to next level: {self.exp_to_next_level}")
        
        return True, level_up_message, stats_message
    
    def update(self):
        """Update player state, including skill cooldowns."""
        # Get current time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        
        # Reduce skill 3 cooldown
        if self.skill3_cooldown > 0:
            self.skill3_cooldown -= 1
        
        # Update position based on velocity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Update collision rect position
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.bottom = self.rect.bottom
        
        # Determine animation state based on current player state
        if self.is_attacking:
            current_state = "attack"
            current_sprites = self.attack_sprites
        elif abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1:  # Check if actually moving
            current_state = "walk"
            current_sprites = self.walk_sprites
            self.moving = True
        else:
            current_state = "idle"
            current_sprites = self.idle_sprites
            self.moving = False
        
        # Reset animation if state changes
        if current_state != self.animation_state:
            self.animation_state = current_state
            self.current_frame = 0
            self.animation_timer = 0
        
        # Update animation timer and frame
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            # Reset timer and advance frame
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(current_sprites)
            
            # Reset attack state after animation completes
            if self.animation_state == "attack" and self.current_frame == 0:
                self.is_attacking = False
        
        # Get the current frame
        self.image = current_sprites[self.current_frame]
        
        # Flip sprite if facing left
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def move(self, dx, dy):
        """Set movement velocity with improved acceleration and normalization."""
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            # Normalize vector to prevent faster diagonal movement
            magnitude = (dx**2 + dy**2)**0.5
            dx = dx / magnitude
            dy = dy / magnitude
        
        # Determine target velocity
        target_vel_x = dx * self.speed
        target_vel_y = dy * self.speed
        
        # Apply acceleration towards target velocity
        self.vel_x = self.vel_x * (1 - self.acceleration) + target_vel_x * self.acceleration
        self.vel_y = self.vel_y * (1 - self.acceleration) + target_vel_y * self.acceleration
        
        # Limit maximum speed
        speed = (self.vel_x**2 + self.vel_y**2)**0.5
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vel_x *= scale
            self.vel_y *= scale
        
        # Update moving state and facing direction
        if abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1:
            self.moving = True
            if self.vel_x > 0:
                self.facing_right = True
            elif self.vel_x < 0:
                self.facing_right = False
        else:
            self.moving = False
            self.vel_x = 0
            self.vel_y = 0
        
        # Update position with current velocity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Apply friction to slow down
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Update collision rect to follow main rect
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.bottom = self.rect.bottom

    def stop(self):
        """Stop movement smoothly."""
        self.vel_x = 0
        self.vel_y = 0
        self.moving = False

    def attack(self):
        """Start attack animation."""
        if not self.is_attacking:
            self.is_attacking = True
            self.current_frame = 0
            self.animation_timer = 0

    def draw_health_bar(self, surface, x=None, y=None):
        """Draw a health bar above the player."""
        # If x and y are not provided, use the player's rect
        if x is None:
            x = self.rect.x
        if y is None:
            y = self.rect.y
        
        bar_width = 80  # Increased from 50 to match larger sprite
        bar_height = 8  # Slightly thicker
        bar_pos = (x + (self.rect.width - bar_width) // 2, y - 15)  # Adjusted vertical position
        
        # Draw background (red)
        pygame.draw.rect(surface, (255, 0, 0), (*bar_pos, bar_width, bar_height))
        
        # Draw health (green)
        health_width = (self.health / self.max_health) * bar_width
        if health_width > 0:
            pygame.draw.rect(surface, (0, 255, 0), (*bar_pos, health_width, bar_height))