import pygame
import os

class Player(pygame.sprite.Sprite):  # Inherit from pygame.sprite.Sprite
    def __init__(self):
        super().__init__()  # Initialize the sprite
        self.x = 300
        self.y = 300
        self.speed = 4
        self.facing_right = True
        self.current_frame = 0
        self.frame_delay = 10
        self.frame_counter = 0
        self.attack_time = 0
        self.skill_time = 0
        self.projectiles = []
        self.arrow_image = pygame.image.load("assets/Arrow.png").convert_alpha()
        self.arrow_image = pygame.transform.scale(self.arrow_image, (50, 10))

        # Load animations
        self.idle_animation = self.load_sprite_sheet("assets/Idle.png", 100, 100, 4)
        self.walk_animation = self.load_sprite_sheet("assets/Walk.png", 100, 100, 6)
        self.attack_animation = self.load_sprite_sheet("assets/Attack.png", 100, 100, 5)
        self.bow_animation = self.load_sprite_sheet("assets/BowAttack.png", 100, 100, 4)
        self.skill2_animation = self.load_sprite_sheet("assets/Skill2.png", 100, 100, 6)

        self.current_animation = self.idle_animation
        self.image = self.current_animation[0]  # Set an initial image for the sprite
        self.rect = self.image.get_rect(topleft=(self.x, self.y))  # Create a rect for collision and positioning

    def load_sprite_sheet(self, sheet_path, frame_width, frame_height, num_frames):
        """Load a sprite sheet, split into frames."""
        if not os.path.exists(sheet_path):
            print(f"Error: File '{sheet_path}' not found!")
            return [pygame.Surface((100, 100))]  # Placeholder frame

        sheet = pygame.image.load(sheet_path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            resized_frame = pygame.transform.scale(frame, (150, 150))
            frames.append(resized_frame)
        return frames

    def handle_movement(self, keys):
        """Handle movement and animation switching."""
        if keys[pygame.K_a]:  
            self.x -= self.speed
            self.current_animation = self.walk_animation
            self.facing_right = False
        elif keys[pygame.K_d]:  
            self.x += self.speed
            self.current_animation = self.walk_animation
            self.facing_right = True
        elif keys[pygame.K_w]:  
            self.y -= self.speed
            self.current_animation = self.walk_animation
        elif keys[pygame.K_s]:  
            self.y += self.speed
            self.current_animation = self.walk_animation
        else:
            self.current_animation = self.idle_animation

        # Update rect position for collision detection
        self.rect.topleft = (self.x, self.y)

    def update_animation(self):
        """Update animation and attack timers."""
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.current_animation)
            self.frame_counter = 0

        # Update the sprite image
        self.image = self.current_animation[self.current_frame]

    def draw(self, screen):
        """Render character and flip if facing left."""
        frame = self.current_animation[self.current_frame]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (self.x, self.y))

    def update_projectiles(self, screen_width, screen_height):
    """Update and remove projectiles that go off-screen."""
    self.projectiles = [proj for proj in self.projectiles if 0 <= proj["x"] <= screen_width]
    for proj in self.projectiles:
        proj["x"] += proj["speed"] if proj["direction"] == "right" else -proj["speed"]
