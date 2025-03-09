import random
from typing import Self

import pygame
from config import GameState, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from entities.player import Player
from entities.enemy import Enemy, GrandMaster
from entities.npc import NPC
from entities.wall import Wall

class GameLogic:
    def __init__(self, battle_system, dialogue_system):
        self.battle_system = battle_system
        self.dialogue_system = dialogue_system
        self.state = GameState.MAIN_MENU
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.player = None
        
    def setup_new_game(self):
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.player)
        
        # Clear existing entities
        self.walls.empty()
        self.enemies.empty()
        self.npcs.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.player)
        
        # Generate a more structured map with walls
        self.generate_map()
        
        # Create some enemies in specific locations
        self.spawn_enemies()
        
        # Create NPCs
        self.spawn_npcs()
        
        self.state = GameState.WORLD
    
    def generate_map(self):
        # Create a border around the map
        wall_thickness = TILE_SIZE
        
        # Top and bottom walls
        for x in range(0, MAP_WIDTH, TILE_SIZE):
            # Top wall
            top_wall = Wall(x, 0, TILE_SIZE, wall_thickness)
            self.walls.add(top_wall)
            self.all_sprites.add(top_wall)
            
            # Bottom wall
            bottom_wall = Wall(x, MAP_HEIGHT - wall_thickness, TILE_SIZE, wall_thickness)
            self.walls.add(bottom_wall)
            self.all_sprites.add(bottom_wall)
        
        # Left and right walls
        for y in range(0, MAP_HEIGHT, TILE_SIZE):
            # Left wall
            left_wall = Wall(0, y, wall_thickness, TILE_SIZE)
            self.walls.add(left_wall)
            self.all_sprites.add(left_wall)
            
            # Right wall
            right_wall = Wall(MAP_WIDTH - wall_thickness, y, wall_thickness, TILE_SIZE)
            self.walls.add(right_wall)
            self.all_sprites.add(right_wall)
        
        # Create some room-like structures
        rooms = [
            (200, 200, 300, 300),  # (x, y, width, height)
            (600, 400, 250, 200),
            (300, 600, 350, 150),
            (800, 200, 200, 400),
            (1200, 300, 350, 350),
            (1500, 600, 300, 250)
        ]
        
        for room in rooms:
            x, y, width, height = room
            # Create walls for the room
            for i in range(0, width, TILE_SIZE):
                # Top and bottom walls
                top_wall = Wall(x + i, y, TILE_SIZE, wall_thickness)
                bottom_wall = Wall(x + i, y + height - wall_thickness, TILE_SIZE, wall_thickness)
                self.walls.add(top_wall, bottom_wall)
                self.all_sprites.add(top_wall, bottom_wall)
            
            for i in range(0, height, TILE_SIZE):
                # Left and right walls
                left_wall = Wall(x, y + i, wall_thickness, TILE_SIZE)
                right_wall = Wall(x + width - wall_thickness, y + i, wall_thickness, TILE_SIZE)
                self.walls.add(left_wall, right_wall)
                self.all_sprites.add(left_wall, right_wall)
                
            # Create door openings
            door_positions = [
                (x + width // 2, y),  # Top
                (x + width // 2, y + height - wall_thickness),  # Bottom
                (x, y + height // 2),  # Left
                (x + width - wall_thickness, y + height // 2)   # Right
            ]
            
            # Randomly choose which walls to remove to create doors
            door_count = random.randint(1, 3)  # Each room has 1-3 doors
            doors = random.sample(door_positions, door_count)
            
            for door_x, door_y in doors:
                # Find and remove walls at door positions
                for wall in list(self.walls):
                    if (wall.rect.x == door_x and wall.rect.y == door_y) or \
                       (wall.rect.x <= door_x < wall.rect.x + wall.rect.width and 
                        wall.rect.y <= door_y < wall.rect.y + wall.rect.height):
                        self.walls.remove(wall)
                        self.all_sprites.remove(wall)
        
        # Add some obstacles inside rooms
        for _ in range(20):
            # Place obstacles away from the player start position
            while True:
                x = random.randint(100, MAP_WIDTH - 100)
                y = random.randint(100, MAP_HEIGHT - 100)
                
                # Check if it's not too close to player
                dx = x - self.player.rect.x
                dy = y - self.player.rect.y
                dist = (dx*dx + dy*dy) ** 0.5
                
                if dist > 200:  # Minimum distance from player
                    break
                    
            obstacle = Wall(x, y, TILE_SIZE, TILE_SIZE)
            self.walls.add(obstacle)
            self.all_sprites.add(obstacle)
    
    def spawn_enemies(self):
        # Create enemies in specific locations
        enemy_positions = [
            (300, 250, "Orc Guard", 50, 10, 25),  # x, y, name, hp, attack, exp
            (700, 450, "Dark Mage", 60, 12, 30),
            (350, 650, "Goblin", 40, 8, 20),
            (850, 250, "Skeleton", 45, 9, 22),
            (1250, 350, "Zombie", 70, 11, 35),
            (1550, 650, "Troll", 80, 15, 40)
        ]
        
        for pos in enemy_positions:
            x, y, name, hp, attack, exp = pos
            enemy = Enemy(x, y, name, hp, attack, exp)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Create the final boss in a specific location
        self.final_boss = GrandMaster(
            MAP_WIDTH - 300, MAP_HEIGHT - 300,
            "Grandmaster Mary-Ann", 300, 20, 500,
            [
                {"name": "Late Penalty", "damage": 15, "effect": "Speed decreased"},
                {"name": "Dark Magic", "damage": 25, "effect": "Critical hit!"},
                {"name": "Harsh Grading", "damage": 20, "effect": "Attack decreased"}
            ]
        )
        self.enemies.add(self.final_boss)
        self.all_sprites.add(self.final_boss)
    
    def spawn_npcs(self):
        # Create NPCs in specific locations
        npc_positions = [
            (400, 400, "Classmate", ["Hey there! Welcome to Lorma School!",
                                   "Watch out for the Grandmasters!",
                                   "Good luck on your journey!"]),
            (800, 600, "Teacher", ["Hello student! Are you prepared for your challenges?",
                                 "The Grandmaster is very powerful.",
                                 "Defeat the enemies to grow stronger!"]),
            (1300, 400, "Old Wizard", ["Welcome to the tower of knowledge!",
                                    "I sense great potential in you.",
                                    "Master your skills to overcome the final test."])
        ]
        
        for pos in npc_positions:
            x, y, name, dialogue = pos
            npc = NPC(x, y, name, dialogue)
            self.npcs.add(npc)
            self.all_sprites.add(npc)
    
    def update_world(self, dx, dy):
        # Move player and check for collisions
        self.player.move(dx, dy, self.walls)
        
        # Update all enemies
        for enemy in self.enemies:
            enemy.update(self.player)
        
        # Update player animations
        self.player.update(self.enemies)
        
        # Check for enemy collision (initiates battle)
        self.check_enemy_collision()
    
    def check_enemy_collision(self):
        # Implement your enemy collision detection logic here
        # This could look something like:
        collided_enemy = pygame.sprite.spritecollideany(self.player, self.enemies)
        if collided_enemy:
            # Start battle
            self.state = GameState.BATTLE
            self.battle_system.start_battle(self.player, collided_enemy)

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