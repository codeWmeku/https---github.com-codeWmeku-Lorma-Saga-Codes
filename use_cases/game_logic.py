import pygame
from entities.player import Player
from entities.enemy import Enemy
from entities.npc import NPC
from frameworks.map_manager import MapManager
from use_cases.battle_system import BattleSystem
from use_cases.dialogue_system import DialogueSystem
from interface_adapters.views.renderer import Camera
from config import GameState, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT

class GameLogic:
    def __init__(self):
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        
        # Initialize game systems
        self.battle_system = BattleSystem()
        self.dialogue_system = DialogueSystem()
        self.map_manager = MapManager()
        
        # Initialize camera
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Set initial game state
        self.state = GameState.MAIN_MENU
        
        # Create player but don't add to sprite group yet
        self.player = Player(400, 300)  # Start position
        
        # Load map tiles
        self.map_manager.load_tileset()
        
        # Initialize last update time
        self.last_update = pygame.time.get_ticks()
        
        # Initialize closest NPC
        self.closest_npc = None
    
    def setup_new_game(self):
        """Initialize a new game."""
        # Clear all sprite groups
        self.all_sprites.empty()
        self.enemies.empty()
        self.npcs.empty()
        self.walls.empty()
        
        # Generate map
        self.tiles, self.walls = self.map_manager.generate_map()
        
        # Add player to sprite group
        self.all_sprites.add(self.player)
        
        # Add some NPCs
        npc1 = NPC(200, 200, "Village Elder", [
            "Welcome to our village, young warrior!",
            "These are dangerous times...",
            "Be careful on your journey."
        ])
        npc2 = NPC(600, 400, "Merchant", [
            "Hello there! Looking to trade?",
            "I have the finest goods in all the land!",
            "Come back anytime!"
        ])
        self.npcs.add(npc1, npc2)
        self.all_sprites.add(npc1, npc2)
        
        # Spawn multiple enemies
        self.spawn_enemies()
        
        # Add walls to all_sprites
        for wall in self.walls:
            self.all_sprites.add(wall)
        
        # Update camera to follow player
        self.camera.update(self.player)
        
        # Change state to world
        self.state = GameState.WORLD
    
    def spawn_enemies(self):
        # Create a wide variety of enemies in multiple locations across the map
        enemy_positions = [
            # Orc Encampment
            (300, 250, "Orc Guard", 50, 10, 25),
            (350, 300, "Orc Warrior", 55, 12, 30),
            (250, 200, "Orc Archer", 45, 8, 20),
            
            # Dark Mage Area
            (700, 450, "Dark Mage", 60, 12, 30),
            (750, 500, "Shadow Apprentice", 40, 9, 22),
            (650, 400, "Necromancer", 70, 15, 35),
            
            # Goblin Territory
            (350, 650, "Goblin", 40, 8, 20),
            (400, 700, "Goblin Scout", 35, 6, 15),
            (300, 600, "Goblin Shaman", 45, 10, 25),
            
            # Undead Zone
            (850, 250, "Skeleton", 45, 9, 22),
            (900, 300, "Skeleton Archer", 40, 7, 18),
            (800, 200, "Skeletal Knight", 60, 12, 30),
            
            # Zombie Swamp
            (1250, 350, "Zombie", 70, 11, 35),
            (1300, 400, "Zombie Brute", 80, 13, 40),
            (1200, 300, "Plague Zombie", 65, 10, 30),
            
            # Troll Mountains
            (1550, 650, "Troll", 80, 15, 40),
            (1600, 700, "Mountain Troll", 90, 17, 45),
            (1500, 600, "Troll Berserker", 85, 16, 42),
            
            # Additional Areas
            (500, 100, "Forest Bandit", 55, 11, 28),
            (1000, 800, "Desert Raider", 60, 12, 32),
            (200, 750, "Mountain Golem", 100, 20, 50),
            (1700, 200, "Ice Witch", 65, 14, 35),
            (50, 500, "Wild Werewolf", 75, 16, 38),
            (1800, 600, "Thunder Mage", 55, 13, 30),
            
            # Random scattered enemies
            (600, 100, "Wandering Mercenary", 50, 10, 25),
            (1100, 450, "Lost Warrior", 55, 11, 28),
            (250, 800, "Rogue Assassin", 45, 9, 22),
            (1600, 100, "Cursed Knight", 70, 14, 35)
        ]
        
        for pos in enemy_positions:
            x, y, name, hp, attack, exp = pos
            enemy = Enemy(x, y, name, hp, attack, exp)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Create the final boss in a specific location
        self.final_boss = Enemy(
            MAP_WIDTH - 300, MAP_HEIGHT - 300,
            "Grandmaster Mary-Ann", 300, 20, 500,
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
    
    def update_world(self, dx, dy):
        """Update the world state."""
        # Move player and check for collisions
        self.player.move(dx, dy, self.walls)
        
        # Update all enemies
        for enemy in self.enemies:
            enemy.update(self.player)
        
        # Update player animations
        self.player.update(self.enemies)
        
        # Check for enemy collision (initiates battle)
        self.check_enemy_collision()
        
        # Check for NPC interaction
        self.check_npc_interaction()
        
        # Update camera to follow player
        self.camera.update(self.player)
    
    def handle_key_event(self, event):
        """Handle specific key events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_3:
                # Use skill 3 (health regeneration)
                if self.player.use_skill3():
                    print(f"Used health regeneration. Current health: {self.player.health}")
    
    def check_enemy_collision(self):
        # Implement your enemy collision detection logic here
        # This could look something like:
        collided_enemy = pygame.sprite.spritecollideany(self.player, self.enemies)
        if collided_enemy:
            # Start battle
            self.state = GameState.BATTLE
            self.battle_system.start_battle(self.player, collided_enemy)

    def check_npc_interaction(self):
        """Check for nearby NPCs and initiate dialogue if in range."""
        if self.state != GameState.WORLD:
            return
            
        # Define interaction range
        INTERACTION_RANGE = 100
        
        # Check each NPC
        for npc in self.npcs:
            # Calculate distance to NPC
            dx = npc.rect.centerx - self.player.rect.centerx
            dy = npc.rect.centery - self.player.rect.centery
            distance = (dx * dx + dy * dy) ** 0.5
            
            # Store the closest NPC in range for interaction
            if distance < INTERACTION_RANGE:
                self.closest_npc = npc
                return
        
        # If no NPC in range, clear the closest NPC
        self.closest_npc = None
    
    def handle_battle_input(self, action_type: str):
        """Handle battle actions from player input.
        
        Args:
            action_type (str): Type of action ("basic_attack" or "skill")
        """
        if self.state != GameState.BATTLE:
            return
            
        result = None
        if action_type == "basic_attack":
            result = self.battle_system.player_attack("basic")
        elif action_type == "skill":
            result = self.battle_system.player_attack("skill")
            
        # Handle battle results
        if result == "victory":
            # Remove all defeated enemies
            defeated_enemies = [enemy for enemy in self.battle_system.enemies if enemy.health <= 0]
            for enemy in defeated_enemies:
                enemy.kill()  # This removes it from all sprite groups
            
            # Return to world state
            self.state = GameState.WORLD
    
    def handle_dialogue_input(self):
        """Handle advancing through dialogue."""
        if self.state != GameState.DIALOGUE:
            return
            
        # Advance dialogue and check if it's finished
        if self.dialogue_system.advance_dialogue():
            self.state = GameState.WORLD  # Ensure we transition back to world state
            self.dialogue_system.end_dialogue()  # Make sure dialogue is properly cleaned up
    
    def handle_movement(self, dx, dy):
        """Handle player movement and collision."""
        if self.state != GameState.WORLD:
            return
            
        # Store original position
        original_x = self.player.rect.x
        original_y = self.player.rect.y
        
        # Update player position
        self.player.move(dx, dy)
        
        # Check wall collisions
        collision_occurred = False
        for wall in self.walls:
            if self.player.collision_rect.colliderect(wall.rect):
                collision_occurred = True
                break
        
        # If collision occurred, restore original position
        if collision_occurred:
            self.player.rect.x = original_x
            self.player.rect.y = original_y
            self.player.collision_rect.centerx = self.player.rect.centerx
            self.player.collision_rect.bottom = self.player.rect.bottom
        
        # Keep player in bounds of the map
        map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        if not map_rect.contains(self.player.rect):
            self.player.rect.clamp_ip(map_rect)
            self.player.collision_rect.centerx = self.player.rect.centerx
            self.player.collision_rect.bottom = self.player.rect.bottom
        
        # Update camera to follow player
        self.camera.update(self.player)
    
    def handle_interaction(self):
        """Handle player interaction with NPCs."""
        if self.state != GameState.WORLD or not self.closest_npc:
            return
            
        # Start dialogue with the closest NPC
        self.state = GameState.DIALOGUE
        self.dialogue_system.start_dialogue(self.closest_npc.dialogue_lines)
    
    def update(self):
        """Update game state."""
        current_time = pygame.time.get_ticks()
        
        if self.state == GameState.WORLD:
            # Update all sprites
            self.all_sprites.update()
            
            # Check for collisions
            self.check_enemy_collision()
            self.check_npc_interaction()
            
            # Check player health
            self.check_player_health()
        
        elif self.state == GameState.BATTLE:
            self.battle_system.update()
            
            # Check if battle is over
            if self.battle_system.is_battle_over():
                self.state = GameState.WORLD
                
        elif self.state == GameState.DIALOGUE:
            self.dialogue_system.update()
            
            # Check if dialogue is finished
            if self.dialogue_system.is_dialogue_finished():
                self.state = GameState.WORLD
        
        # Update last update time
        self.last_update = current_time
    
    def handle_attack(self):
        """Handle player attack input."""
        if self.state == GameState.WORLD:
            self.player.attack()
    
    def start_battle(self, enemy):
        """Start a battle with an enemy."""
        if self.state == GameState.WORLD:
            self.state = GameState.BATTLE
            self.battle_system.start_battle(self.player, enemy)
    
    def render(self, screen):
        """Render the game world with camera tracking."""
        # Update camera to follow player
        self.camera.update(self.player)
        
        # Clear the screen
        screen.fill((0, 0, 0))  # Black background
        
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu(screen)
        
        elif self.state == GameState.WORLD:
            # Render map tiles with camera offset
            for tile in self.tiles:
                screen.blit(tile.image, self.camera.apply(tile))
            
            # Render walls with camera offset
            for wall in self.walls:
                screen.blit(wall.image, self.camera.apply(wall))
            
            # Render player 
            screen.blit(self.player.image, self.camera.apply(self.player))
            
            # Render enemies with camera offset
            for enemy in self.enemies:
                screen.blit(enemy.image, self.camera.apply(enemy))
            
            # Render NPCs with camera offset
            for npc in self.npcs:
                screen.blit(npc.image, self.camera.apply(npc))
        
        elif self.state == GameState.DIALOGUE:
            # Render map tiles with camera offset
            for tile in self.tiles:
                screen.blit(tile.image, self.camera.apply(tile))
            
            # Render walls with camera offset
            for wall in self.walls:
                screen.blit(wall.image, self.camera.apply(wall))
            
            # Render player with camera offset
            screen.blit(self.player.image, self.camera.apply(self.player))
            
            # Render enemies with camera offset
            for enemy in self.enemies:
                screen.blit(enemy.image, self.camera.apply(enemy))
            
            # Render NPCs with camera offset
            for npc in self.npcs:
                screen.blit(npc.image, self.camera.apply(npc))
            
            # Render dialogue box
            self.dialogue_system.render(screen)
        
        elif self.state == GameState.BATTLE:
            # Render battle screen
            self.battle_system.draw(screen)
            
        elif self.state == GameState.GAME_OVER:
            # Render game over screen
            self.draw_game_over(screen)
        
        # Update display
        pygame.display.flip()

    def draw_main_menu(self, screen):
        """Draw the main menu screen."""
        # Fill background
        screen.fill((0, 0, 0))
        
        # Create font
        font = pygame.font.Font(None, 74)
        
        # Draw title
        title = font.render("Lorma Saga", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
        screen.blit(title, title_rect)
        
        # Draw start prompt
        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Start", True, (255, 255, 255))
        prompt_rect = prompt.get_rect(center=(screen.get_width() // 2, screen.get_height() * 2 // 3))
        screen.blit(prompt, prompt_rect)
    
    def draw_game_over(self, screen):
        """Draw the game over screen."""
        # Fill background
        screen.fill((0, 0, 0))
        
        # Create font
        font = pygame.font.Font(None, 74)
        
        # Draw game over text
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, text_rect)
        
        # Draw restart prompt
        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Restart", True, (255, 255, 255))
        prompt_rect = prompt.get_rect(center=(screen.get_width() // 2, screen.get_height() * 2 // 3))
        screen.blit(prompt, prompt_rect)
    
    def check_player_health(self):
        """Check if player health has reached 0 and trigger game over."""
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks in the game."""
        return False