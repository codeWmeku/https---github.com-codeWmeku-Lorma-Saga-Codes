import pygame
import random
from entities.player import Player
from entities.enemy import Enemy

from entities.boss import Boss
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
        self.walls = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        
        # Initialize game systems
        self.battle_system = BattleSystem()
        self.dialogue_system = DialogueSystem()
        self.map_manager = MapManager()
        
        # Initialize camera
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Set initial game state
        self.state = GameState.MAIN_MENU
        self.previous_state = None
        
        # Create player but don't add to sprite group yet
        self.player = Player(400, 300)  # Start position
        
        # Load map tiles
        self.map_manager.load_tileset()
        
        # Initialize last update time
        self.last_update = pygame.time.get_ticks()
        

        
        # Initialize player ID selection
        self.selected_player_id = 1
        self.total_players = 5
        self.player_selection_active = False
        
        # Audio settings
        self.music_volume = 0.5  # Default volume (0.0 to 1.0)
        self.volume_slider_rect = None
        self.volume_handle_rect = None
        self.volume_dragging = False
        
        # Initialize pause UI elements
        self.resume_button_rect = None
        self.pause_button_rect = None
        self.pause_background = None
        self.capture_screen_for_pause = False
    
    def setup_new_game(self):
        """Initialize a new game."""
        # Clear all sprite groups
        self.all_sprites.empty()
        self.enemies.empty()
        self.walls.empty()
        self.bosses.empty()
        
        # Generate map
        self.tiles, self.walls = self.map_manager.generate_map()
        
        # Set player ID based on selection
        self.player.set_player_id(self.selected_player_id)
        
        # Add player to sprite group
        self.all_sprites.add(self.player)
        
        # Show opening story dialogue
        self.show_opening_story()
        

        
        # Spawn multiple enemies
        self.spawn_enemies()
        
        # Spawn the boss
        self.spawn_boss()
        
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
    
    def spawn_boss(self):
        """Spawn the Mzana boss in a specific location on the map."""
        # Position the boss in a dramatic location (center of a special area)
        boss_x = MAP_WIDTH - 300
        boss_y = MAP_HEIGHT - 300
        
        # Create the Mzana boss with high health and attack power
        mzana = Boss(boss_x, boss_y, name="Mzana", health=500, attack=25, exp=150)
        
        # Add to sprite groups
        self.bosses.add(mzana)
        self.all_sprites.add(mzana)
        
        print(f"Boss '{mzana.name}' spawned at ({boss_x}, {boss_y})")
    

        
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
        

        
        # Update camera to follow player
        self.camera.update(self.player)
    
    def handle_key_event(self, event):
        """Handle specific key events."""
        if event.type == pygame.KEYDOWN:
            # Global pause handling (works in any non-menu state)
            if event.key == pygame.K_ESCAPE and self.state not in [GameState.MAIN_MENU, GameState.GAME_OVER]:
                if self.state == GameState.PAUSED:
                    # Resume the game by returning to previous state
                    if hasattr(self, 'previous_state'):
                        self.state = self.previous_state
                        # Clear the pause background to free memory
                        if hasattr(self, 'pause_background'):
                            self.pause_background = None
                else:
                    # Take a screenshot of the current screen to use as pause background
                    # This will happen on next render cycle
                    self.capture_screen_for_pause = True
                    # Pause the game and store previous state
                    self.previous_state = self.state
                    self.state = GameState.PAUSED
                return
            
            # Handle Enter key in Game Over state to restart the game
            if self.state == GameState.GAME_OVER and event.key == pygame.K_RETURN:
                print("Restarting game after Game Over")
                # Reset player stats
                self.player.health = self.player.max_health  # Restore full health
                self.player.skill3_cooldown = 0  # Reset healing cooldown
                # Start a new game
                self.setup_new_game()
                return
                
            if self.state == GameState.MAIN_MENU:
                if event.key == pygame.K_UP:
                    # Toggle player selection mode
                    self.player_selection_active = not self.player_selection_active
                elif event.key == pygame.K_LEFT and self.player_selection_active:
                    # Decrease player ID (with wraparound)
                    self.selected_player_id = ((self.selected_player_id - 2) % self.total_players) + 1
                elif event.key == pygame.K_RIGHT and self.player_selection_active:
                    # Increase player ID (with wraparound)
                    self.selected_player_id = (self.selected_player_id % self.total_players) + 1
                elif event.key == pygame.K_RETURN:
                    # Start the game with selected player ID
                    self.setup_new_game()
            elif self.state == GameState.BATTLE:
                if event.key == pygame.K_3:
                    # Use healing skill in battle
                    self.battle_system.process_heal()
            elif self.state == GameState.WORLD:
                if event.key == pygame.K_3:
                    # Use skill 3 (health regeneration) in world
                    if self.player.use_skill3():
                        print(f"Used health regeneration. Current health: {self.player.health}")
            elif self.state == GameState.PAUSED:
                # Handle additional pause-state specific inputs here if needed
                pass
    
    def check_enemy_collision(self):
        # Check collisions with regular enemies
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.start_battle(enemy)
                break
                
        # Check collisions with boss enemies
        for boss in self.bosses:
            if self.player.rect.colliderect(boss.rect):
                self.start_battle(boss)
                break
                
    def start_battle(self, enemy):
        """Start a battle with an enemy."""
        self.state = GameState.BATTLE
        self.battle_system.start_battle(self.player, enemy)
        

    
    def handle_battle_input(self, action_type: str):
        """Handle battle actions from player input.
        
        Args:
            action_type (str): Type of action ("basic_attack", "skill", or "heal")
        """
        if self.state != GameState.BATTLE:
            return
        
        if action_type == "basic_attack":
            result = self.battle_system.player_attack("basic")
        elif action_type == "skill":
            result = self.battle_system.player_attack("skill")
        elif action_type == "heal":
            result = self.battle_system.process_heal()
            
        # Handle battle results
        if result == "victory":
            # Remove all defeated enemies
            defeated_enemies = [enemy for enemy in self.battle_system.enemies if enemy.health <= 0]
            for enemy in defeated_enemies:
                enemy.kill()  # This removes it from all sprite groups
            
            # Check if player gained enough XP to level up
            if hasattr(self.player, 'exp') and hasattr(self.player, 'gain_exp'):
                # When player defeats an enemy, gains XP based on enemy's level/difficulty
                for enemy in defeated_enemies:
                    if hasattr(enemy, 'exp_reward'):
                        exp_gained = enemy.exp_reward
                    else:
                        # Default XP if enemy doesn't have a specific reward
                        exp_gained = 25
                    
                    # Apply XP gain and check for level up
                    leveled_up = self.player.gain_exp(exp_gained)
                    
                    if leveled_up:
                        # Show level up notification
                        self.show_level_up_notification()
            
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
    

    
    def update(self):
        """Update game state."""
        current_time = pygame.time.get_ticks()
        time_delta = current_time - self.last_update
        self.last_update = current_time
        
        # Handle volume slider dragging (in any state)
        if self.volume_dragging:
            # Get mouse state (position and button state)
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            
            # If left mouse button is held down, update the slider
            if mouse_buttons[0]:  # Left button still pressed
                # Update volume based on mouse position
                slider_x = self.volume_slider_rect.x
                slider_width = self.volume_slider_rect.width
                new_volume = max(0, min(1, (mouse_pos[0] - slider_x) / slider_width))
                self.music_volume = new_volume
                
                # Update the handle position
                handle_size = self.volume_handle_rect.width
                handle_x = slider_x + int(self.music_volume * slider_width)
                self.volume_handle_rect.x = handle_x - handle_size // 2
                
                # Apply the volume change to the music
                pygame.mixer.music.set_volume(self.music_volume)
            else:
                # Mouse button released, end dragging
                self.volume_dragging = False
        
        # Update based on current state
        if self.state == GameState.WORLD:
            # Update all sprites
            if hasattr(self.player, 'update'):
                self.player.update()
            self.all_sprites.update()
            
            # Check for collisions
            self.check_enemy_collision()
            
            # Check player health
            self.check_player_health()
            
            # Update skill cooldowns
            if hasattr(self.player, 'skill3_cooldown') and self.player.skill3_cooldown > 0:
                self.player.skill3_cooldown -= 1
        
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
    
    def _render_world(self, screen):
        """Helper method to render the game world with seamless edge wrapping."""
        # Get screen dimensions
        screen_width, screen_height = screen.get_size()
        
        # Calculate camera positions
        camera_x = -self.camera.x_offset
        camera_y = -self.camera.y_offset
        
        # Draw tiles with wrapping for a seamless world
        for tile in self.tiles:
            # Calculate base position with camera offset
            base_x = tile.rect.x + self.camera.x_offset
            base_y = tile.rect.y + self.camera.y_offset
            
            # Calculate modulo positions for wrapping
            wrap_x = base_x % MAP_WIDTH
            wrap_y = base_y % MAP_HEIGHT
            
            # Determine if we need to draw this tile on screen
            if wrap_x < screen_width and wrap_y < screen_height:
                screen.blit(tile.image, (wrap_x, wrap_y))
                
            # Draw additional copies if needed for seamless wrapping
            if wrap_x + tile.rect.width > screen_width:
                screen.blit(tile.image, (wrap_x - MAP_WIDTH, wrap_y))
            if wrap_y + tile.rect.height > screen_height:
                screen.blit(tile.image, (wrap_x, wrap_y - MAP_HEIGHT))
            if wrap_x + tile.rect.width > screen_width and wrap_y + tile.rect.height > screen_height:
                screen.blit(tile.image, (wrap_x - MAP_WIDTH, wrap_y - MAP_HEIGHT))
        
        # Render walls with similar wrapping logic
        for wall in self.walls:
            base_x = wall.rect.x + self.camera.x_offset
            base_y = wall.rect.y + self.camera.y_offset
            screen.blit(wall.image, (base_x, base_y))
            
            # Wrap horizontally if needed
            if base_x < 0:
                screen.blit(wall.image, (base_x + MAP_WIDTH, base_y))
            elif base_x > screen_width - wall.rect.width:
                screen.blit(wall.image, (base_x - MAP_WIDTH, base_y))
                
            # Wrap vertically if needed
            if base_y < 0:
                screen.blit(wall.image, (base_x, base_y + MAP_HEIGHT))
            elif base_y > screen_height - wall.rect.height:
                screen.blit(wall.image, (base_x, base_y - MAP_HEIGHT))
        
        # Render player at center
        screen.blit(self.player.image, self.camera.apply(self.player))
        
        # Render enemies with wrapping behavior
        for enemy in self.enemies:
            base_x = enemy.rect.x + self.camera.x_offset
            base_y = enemy.rect.y + self.camera.y_offset
            
            # Only render if potentially visible
            if -enemy.rect.width <= base_x <= screen_width and -enemy.rect.height <= base_y <= screen_height:
                screen.blit(enemy.image, (base_x, base_y))
                
            # Wrap horizontally if needed
            if base_x < 0:
                screen.blit(enemy.image, (base_x + MAP_WIDTH, base_y))
            elif base_x > screen_width - enemy.rect.width:
                screen.blit(enemy.image, (base_x - MAP_WIDTH, base_y))
                
            # Wrap vertically if needed
            if base_y < 0:
                screen.blit(enemy.image, (base_x, base_y + MAP_HEIGHT))
            elif base_y > screen_height - enemy.rect.height:
                screen.blit(enemy.image, (base_x, base_y - MAP_HEIGHT))
        

            
        # Render bosses with the same wrapping logic
        for boss in self.bosses:
            base_x = boss.rect.x + self.camera.x_offset
            base_y = boss.rect.y + self.camera.y_offset
            
            if -boss.rect.width <= base_x <= screen_width and -boss.rect.height <= base_y <= screen_height:
                screen.blit(boss.image, (base_x, base_y))
                
                # Draw boss health bar
                if hasattr(boss, 'draw_health_bar'):
                    boss.draw_health_bar(screen, base_x, base_y)
                
            # Wrap horizontally if needed
            if base_x < 0:
                screen.blit(boss.image, (base_x + MAP_WIDTH, base_y))
                # Draw health bar for wrapped boss too
                if hasattr(boss, 'draw_health_bar'):
                    boss.draw_health_bar(screen, base_x + MAP_WIDTH, base_y)
            elif base_x > screen_width - boss.rect.width:
                screen.blit(boss.image, (base_x - MAP_WIDTH, base_y))
                if hasattr(boss, 'draw_health_bar'):
                    boss.draw_health_bar(screen, base_x - MAP_WIDTH, base_y)
                
            # Wrap vertically if needed
            if base_y < 0:
                screen.blit(boss.image, (base_x, base_y + MAP_HEIGHT))
                if hasattr(boss, 'draw_health_bar'):
                    boss.draw_health_bar(screen, base_x, base_y + MAP_HEIGHT)
            elif base_y > screen_height - boss.rect.height:
                screen.blit(boss.image, (base_x, base_y - MAP_HEIGHT))
                if hasattr(boss, 'draw_health_bar'):
                    boss.draw_health_bar(screen, base_x, base_y - MAP_HEIGHT)
    
    def draw_pause_screen(self, screen):
        """Draw the pause screen overlay."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Add pause title
        font = pygame.font.Font(None, 64)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
        screen.blit(pause_text, text_rect)
        
        # Button dimensions and spacing
        button_width, button_height = 250, 60
        button_x = (screen.get_width() - button_width) // 2
        button_spacing = 80  # Space between buttons
        
        # Create Resume button (top)
        resume_y = screen.get_height() // 2 - button_spacing
        self.resume_button_rect = pygame.Rect(button_x, resume_y, button_width, button_height)
        
        # Create Main Menu button (middle)
        main_menu_y = screen.get_height() // 2
        self.main_menu_button_rect = pygame.Rect(button_x, main_menu_y, button_width, button_height)
        
        # Create Exit Game button (bottom)
        exit_y = screen.get_height() // 2 + button_spacing
        self.exit_button_rect = pygame.Rect(button_x, exit_y, button_width, button_height)
        
        # Create volume slider (much lower on the screen to avoid overlap)
        volume_y = exit_y + button_spacing + 90  # Increased from 30 to 90 to move it down
        slider_width = 250
        slider_height = 10
        slider_x = (screen.get_width() - slider_width) // 2
        
        # Store slider rect for interaction
        self.volume_slider_rect = pygame.Rect(slider_x, volume_y, slider_width, slider_height)
        
        # Calculate handle position based on current volume
        handle_x = slider_x + int(self.music_volume * slider_width)
        handle_size = 20
        self.volume_handle_rect = pygame.Rect(handle_x - handle_size//2, volume_y - handle_size//2 + slider_height//2, handle_size, handle_size)
        
        # Draw buttons with hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw Resume button
        resume_color = (0, 120, 220) if self.resume_button_rect.collidepoint(mouse_pos) else (0, 100, 200)
        pygame.draw.rect(screen, resume_color, self.resume_button_rect)
        pygame.draw.rect(screen, (100, 200, 255), self.resume_button_rect.inflate(-10, -10))
        pygame.draw.rect(screen, (255, 255, 255), self.resume_button_rect, 3)  # White border
        
        # Draw Main Menu button
        menu_color = (120, 120, 220) if self.main_menu_button_rect.collidepoint(mouse_pos) else (100, 100, 200)
        pygame.draw.rect(screen, menu_color, self.main_menu_button_rect)
        pygame.draw.rect(screen, (150, 150, 255), self.main_menu_button_rect.inflate(-10, -10))
        pygame.draw.rect(screen, (255, 255, 255), self.main_menu_button_rect, 3)  # White border
        
        # Draw Exit button
        exit_color = (220, 80, 80) if self.exit_button_rect.collidepoint(mouse_pos) else (200, 60, 60)
        pygame.draw.rect(screen, exit_color, self.exit_button_rect)
        pygame.draw.rect(screen, (255, 120, 120), self.exit_button_rect.inflate(-10, -10))
        pygame.draw.rect(screen, (255, 255, 255), self.exit_button_rect, 3)  # White border
        
        # Draw button texts
        font = pygame.font.Font(None, 40)
        
        # Resume button text
        resume_text = font.render("RESUME", True, (255, 255, 255))
        resume_text_rect = resume_text.get_rect(center=self.resume_button_rect.center)
        screen.blit(resume_text, resume_text_rect)
        
        # Main Menu button text
        menu_text = font.render("MAIN MENU", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=self.main_menu_button_rect.center)
        screen.blit(menu_text, menu_text_rect)
        
        # Exit button text
        exit_text = font.render("EXIT GAME", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=self.exit_button_rect.center)
        screen.blit(exit_text, exit_text_rect)
        
        # Draw volume control slider
        font_small = pygame.font.Font(None, 30)
        volume_text = font_small.render("Music Volume", True, (255, 255, 255))
        volume_text_rect = volume_text.get_rect(center=(screen.get_width() // 2, self.volume_slider_rect.y - 20))
        screen.blit(volume_text, volume_text_rect)
        
        # Draw slider track
        pygame.draw.rect(screen, (100, 100, 100), self.volume_slider_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.volume_slider_rect, 1)
        
        # Draw filled portion of the slider
        filled_width = int(self.music_volume * self.volume_slider_rect.width)
        filled_rect = pygame.Rect(self.volume_slider_rect.x, self.volume_slider_rect.y, filled_width, self.volume_slider_rect.height)
        pygame.draw.rect(screen, (100, 150, 255), filled_rect)
        
        # Draw slider handle
        pygame.draw.circle(screen, (150, 200, 255), self.volume_handle_rect.center, self.volume_handle_rect.width//2)
        pygame.draw.circle(screen, (255, 255, 255), self.volume_handle_rect.center, self.volume_handle_rect.width//2, 2)
        
        # Show current volume percentage
        volume_percent = int(self.music_volume * 100)
        percent_text = font_small.render(f"{volume_percent}%", True, (255, 255, 255))
        percent_rect = percent_text.get_rect(midleft=(self.volume_slider_rect.right + 10, self.volume_slider_rect.centery))
        screen.blit(percent_text, percent_rect)
        
        # ESC key instructions positioned above the volume slider
        font = pygame.font.Font(None, 28)
        instructions = font.render("Press ESC to Resume", True, (255, 255, 255))
        instructions_rect = instructions.get_rect(center=(screen.get_width() // 2, exit_y + button_height + 50))
        screen.blit(instructions, instructions_rect)
        
        # Controls reminder removed as requested
    
    def render(self, screen):
        """Render the game world with camera tracking."""
        # Check if we need to capture the screen for pause
        if self.capture_screen_for_pause and self.state == GameState.PAUSED:
            # We want to make sure the screen is fully rendered before capturing
            # So we'll render the previous state first
            if hasattr(self, 'previous_state') and self.previous_state is not None:
                temp_state = self.state
                self.state = self.previous_state  # Temporarily set to previous state
                
                # Update camera to follow player
                self.camera.update(self.player)
                
                # Clear the screen
                screen.fill((0, 0, 0))  # Black background
                
                # Do a normal render of the previous state
                if self.state == GameState.MAIN_MENU:
                    self.draw_main_menu(screen)
                elif self.state == GameState.WORLD:
                    self._render_world(screen)
                elif self.state == GameState.DIALOGUE:
                    self._render_world(screen)
                    self.dialogue_system.render(screen)
                elif self.state == GameState.BATTLE:
                    self.battle_system.draw(screen)
                
                # Capture the current screen content
                self.pause_background = screen.copy()
                
                # Reset to pause state
                self.state = temp_state
                self.capture_screen_for_pause = False  # Turn off capture flag
                
                # Apply a darkening/blur effect to the background
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))  # Semi-transparent black
                self.pause_background.blit(overlay, (0, 0))
                
                # Now render the pause menu over this background
                screen.blit(self.pause_background, (0, 0))
                self.draw_pause_screen(screen)
                return
        
        # Update camera to follow player
        self.camera.update(self.player)
        
        # Clear the screen
        screen.fill((0, 0, 0))  # Black background
        
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu(screen)
        
        elif self.state == GameState.WORLD:
            self._render_world(screen)
            
            # Display player level and experience information
            font = pygame.font.Font(None, 24)
            level_text = font.render(f"Level: {self.player.level}", True, (255, 255, 255))
            screen.blit(level_text, (10, 10))
            
            # Display experience as a progress bar
            exp_bar_width = 150
            exp_bar_height = 15
            exp_text = font.render(f"EXP: {self.player.exp}/{self.player.exp_to_next_level}", True, (255, 255, 255))
            screen.blit(exp_text, (10, 40))
            
            # Draw exp bar background
            pygame.draw.rect(screen, (80, 80, 80), (10, 70, exp_bar_width, exp_bar_height))
            
            # Calculate current progress
            if self.player.exp_to_next_level > 0:  # Avoid division by zero
                exp_progress = min(1.0, self.player.exp / self.player.exp_to_next_level)
                if exp_progress > 0:
                    # Draw filled portion of exp bar
                    pygame.draw.rect(screen, (100, 200, 255), 
                                    (10, 70, int(exp_bar_width * exp_progress), exp_bar_height))
            
            # Display heal cooldown in the world state if applicable
            if hasattr(self.player, 'skill3_cooldown') and self.player.skill3_cooldown > 0:
                cooldown_text = font.render(f"Heal Cooldown: {self.player.skill3_cooldown//60 + 1}s", True, (255, 200, 200))
                screen.blit(cooldown_text, (10, 95))
        
        elif self.state == GameState.DIALOGUE:
            # Render the world first
            self._render_world(screen)
            
            # Render dialogue box on top
            self.dialogue_system.render(screen)
        
        elif self.state == GameState.BATTLE:
            # Render battle screen
            self.battle_system.draw(screen)
            
        elif self.state == GameState.GAME_OVER:
            # Render game over screen
            self.draw_game_over(screen)
            
        elif self.state == GameState.PAUSED:
            # Instead of recursive rendering, use a snapshot approach
            # If we don't have a snapshot, just render a plain background
            if not hasattr(self, 'pause_background') or self.pause_background is None:
                # Fill with a plain dark background
                screen.fill((20, 20, 40))  # Dark blue-gray background
                
                # Draw some decorative elements for visual interest
                for i in range(10):
                    x = random.randint(0, screen.get_width())
                    y = random.randint(0, screen.get_height())
                    size = random.randint(2, 5)
                    pygame.draw.circle(screen, (255, 255, 255, 50), (x, y), size)
            else:
                # Use the existing snapshot
                screen.blit(self.pause_background, (0, 0))
            
            # Then overlay pause screen
            self.draw_pause_screen(screen)
        
        # Add Pause Button in all gameplay states
        if self.state in [GameState.WORLD, GameState.BATTLE, GameState.DIALOGUE]:
            # Store pause button data for click detection
            pause_btn_pos = (screen.get_width() - 80, 20)
            pause_btn_size = (60, 30)
            self.pause_button_rect = pygame.Rect(pause_btn_pos, pause_btn_size)
            
            # Draw button with highlight on hover
            mouse_pos = pygame.mouse.get_pos()
            button_color = (120, 120, 200) if self.pause_button_rect.collidepoint(mouse_pos) else (80, 80, 120)
            
            # Draw button with 3D effect
            pygame.draw.rect(screen, button_color, self.pause_button_rect)
            pygame.draw.rect(screen, (200, 200, 255), self.pause_button_rect, 2)  # Bright border
            
            # Add shadow effect
            shadow_rect = self.pause_button_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(screen, (40, 40, 60), shadow_rect, 1)
            
            # Draw button text
            font = pygame.font.Font(None, 24)
            pause_text = font.render("PAUSE", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=self.pause_button_rect.center)
            screen.blit(pause_text, text_rect)
        
        # Update display
        pygame.display.flip()

    def draw_main_menu(self, screen):
        """Draw the main menu screen with the game map as the background."""
        if not hasattr(self, 'tiles'):
            # If tiles haven't been generated yet, create them for the background
            self.map_manager.load_tileset()  # Make sure to load the tileset if not already loaded
            self.tiles, _ = self.map_manager.generate_map()

        # Render the map tiles to the screen (without camera offset for the main menu)
        for tile in self.tiles:
            screen.blit(tile.image, (tile.rect.x, tile.rect.y))

        # Create fade effect for better text contrast - use actual screen dimensions
        screen_width, screen_height = screen.get_size()
        fade_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 180))  # Semi-transparent overlay
        screen.blit(fade_surface, (0, 0))

        # Create font for title and draw with some scale/animation
        font = pygame.font.Font(None, 96)  # Larger font for title
        title_text = font.render("Lorma Saga", True, (255, 255, 255))  # White color for the title
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))

        # Add animation effect (title appearing from a smaller size to normal)
        scale_factor = 1.2  # Initial scale size
        scaled_title = pygame.transform.scale(title_text, (int(title_rect.width * scale_factor), int(title_rect.height * scale_factor)))
        title_rect = scaled_title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
        
        screen.blit(scaled_title, title_rect)

        # Draw player selection interface
        self.draw_player_selection(screen)
        
        # Start prompt with improved font and hover effect
        font = pygame.font.Font(None, 48)
        prompt_text = font.render("Press ENTER to Start", True, (255, 255, 255))
        prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() * 3 // 4))

        # Hover effect (change color when mouse is over)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if prompt_rect.collidepoint(mouse_x, mouse_y):
            prompt_text = font.render("Press ENTER to Start", True, (0, 255, 0))  # Change color to green
        
        screen.blit(prompt_text, prompt_rect)
        
        # Add volume control slider at the bottom of the screen
        volume_y = screen.get_height() - 70
        slider_width = 250
        slider_height = 10
        slider_x = (screen.get_width() - slider_width) // 2
        
        # Store slider rect for interaction
        self.volume_slider_rect = pygame.Rect(slider_x, volume_y, slider_width, slider_height)
        
        # Calculate handle position based on current volume
        handle_x = slider_x + int(self.music_volume * slider_width)
        handle_size = 20
        self.volume_handle_rect = pygame.Rect(handle_x - handle_size//2, volume_y - handle_size//2 + slider_height//2, handle_size, handle_size)
        
        # Draw volume control label
        font_small = pygame.font.Font(None, 30)
        volume_text = font_small.render("Music Volume", True, (255, 255, 255))
        volume_text_rect = volume_text.get_rect(center=(screen.get_width() // 2, volume_y - 20))
        screen.blit(volume_text, volume_text_rect)
        
        # Draw slider track
        pygame.draw.rect(screen, (100, 100, 100), self.volume_slider_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.volume_slider_rect, 1)
        
        # Draw filled portion of the slider
        filled_width = int(self.music_volume * self.volume_slider_rect.width)
        filled_rect = pygame.Rect(self.volume_slider_rect.x, self.volume_slider_rect.y, filled_width, self.volume_slider_rect.height)
        pygame.draw.rect(screen, (200, 150, 255), filled_rect)
        
        # Draw slider handle
        pygame.draw.circle(screen, (200, 150, 255), self.volume_handle_rect.center, self.volume_handle_rect.width//2)
        pygame.draw.circle(screen, (255, 255, 255), self.volume_handle_rect.center, self.volume_handle_rect.width//2, 2)
        
        # Show current volume percentage
        volume_percent = int(self.music_volume * 100)
        percent_text = font_small.render(f"{volume_percent}%", True, (255, 255, 255))
        percent_rect = percent_text.get_rect(midleft=(self.volume_slider_rect.right + 10, self.volume_slider_rect.centery))
        screen.blit(percent_text, percent_rect)
        
        # Instructions for player selection
        font = pygame.font.Font(None, 28)
        instructions_text = font.render("Press UP to toggle player selection, LEFT/RIGHT to change player", True, (200, 200, 200))
        instructions_rect = instructions_text.get_rect(center=(screen.get_width() // 2, screen.get_height() * 7 // 8))
        screen.blit(instructions_text, instructions_rect)

    def show_opening_story(self):
        """Show the opening storyline dialogue to introduce the game's story."""
        # Create a generic opening story
        story_lines = [
            f"Welcome to Lorma Saga, Player {self.selected_player_id}!",
            "The school has been overtaken by the Grandmasters, powerful beings who have corrupted our once peaceful halls.",
            "Your mission is to defeat the enemies scattered throughout the campus and ultimately confront Grandmaster Mary-Ann.",
            "Good luck on your journey!"
        ]
        
        # Start dialogue with the opening story
        self.state = GameState.DIALOGUE
        self.dialogue_system.start_dialogue(story_lines)
        
    def draw_player_selection(self, screen):
        """Draw the player selection interface on the main menu."""
        # Create player selection box
        selection_box_width = 600
        selection_box_height = 300
        selection_box_x = (screen.get_width() - selection_box_width) // 2
        selection_box_y = screen.get_height() // 2 - selection_box_height // 2
        
        # Draw selection box background with slight transparency
        selection_surface = pygame.Surface((selection_box_width, selection_box_height), pygame.SRCALPHA)
        if self.player_selection_active:
            selection_surface.fill((0, 100, 200, 180))  # Blue when active
        else:
            selection_surface.fill((100, 100, 100, 150))  # Gray when inactive
        
        # Draw selection box border
        pygame.draw.rect(selection_surface, (255, 255, 255), (0, 0, selection_box_width, selection_box_height), 3)
        screen.blit(selection_surface, (selection_box_x, selection_box_y))
        
        # Draw "Choose Your Character" title
        font = pygame.font.Font(None, 42)
        title_text = font.render("Choose Your Character", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(selection_box_x + selection_box_width // 2, selection_box_y + 30))
        screen.blit(title_text, title_rect)
        
        # Draw player selection buttons
        button_width = 60
        button_spacing = 30
        total_buttons_width = (button_width * self.total_players) + (button_spacing * (self.total_players - 1))
        start_x = selection_box_x + (selection_box_width - total_buttons_width) // 2
        button_y = selection_box_y + 80
        
        # Instructions for player selection
        instruction_font = pygame.font.Font(None, 28)
        instruction_text = instruction_font.render("Press UP to activate selection, LEFT/RIGHT to choose, ENTER to start", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(selection_box_x + selection_box_width // 2, selection_box_y + selection_box_height - 30))
        screen.blit(instruction_text, instruction_rect)
        
        for i in range(1, self.total_players + 1):
            button_x = start_x + (i - 1) * (button_width + button_spacing)
            
            # Draw button background
            button_color = (0, 200, 0) if i == self.selected_player_id else (150, 150, 150)
            if self.player_selection_active and i == self.selected_player_id:
                # Add a glow effect when active and selected
                glow_surface = pygame.Surface((button_width + 8, button_width + 8), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 255, 0, 100), (button_width // 2 + 4, button_width // 2 + 4), button_width // 2 + 4)
                screen.blit(glow_surface, (button_x - 4, button_y - 4))
            
            pygame.draw.circle(screen, button_color, (button_x + button_width // 2, button_y + button_width // 2), button_width // 2)
            
            # Draw player number
            number_font = pygame.font.Font(None, 36)
            number_text = number_font.render(str(i), True, (255, 255, 255))
            number_rect = number_text.get_rect(center=(button_x + button_width // 2, button_y + button_width // 2))
            screen.blit(number_text, number_rect)
        
        # Display selected player message
        info_font = pygame.font.Font(None, 32)
        name_font = pygame.font.Font(None, 48)
        
        # Player title
        title_text = name_font.render(f"Player {self.selected_player_id}", True, (255, 255, 0))
        title_rect = title_text.get_rect(center=(selection_box_x + selection_box_width // 2, selection_box_y + 170))
        screen.blit(title_text, title_rect)
        
        # Selection status
        status_text = info_font.render(
            "Selection Active" if self.player_selection_active else "Press UP to activate selection", 
            True, 
            (0, 255, 0) if self.player_selection_active else (255, 255, 255)
        )
        status_rect = status_text.get_rect(center=(selection_box_x + selection_box_width // 2, selection_box_y + 220))
        screen.blit(status_text, status_rect)
    
    def show_level_up_notification(self):
        """Display a notification when the player levels up."""
        # Get level up messages from player's level_up method
        success, level_up_msg, stats_msg = self.player.level_up()
        
        if success:
            # Create more prominent dialogue messages for level up notification
            level_up_dialogue = [
                "***** LEVEL UP! *****",
                level_up_msg,
                stats_msg,
                "Your character has grown stronger!",
                "Press Enter to continue your adventure!"
            ]
            
            # Sound effect for level up could be added here
            # if pygame.mixer.get_init():
            #     level_up_sound = pygame.mixer.Sound('assets/sounds/level_up.wav')
            #     level_up_sound.play()
            
            # Show the level up notification as dialogue
            self.previous_state = self.state
            self.state = GameState.DIALOGUE
            self.dialogue_system.start_dialogue(level_up_dialogue)
    
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
        
        # Draw restart prompt with button
        button_width, button_height = 300, 60
        button_x = (screen.get_width() - button_width) // 2
        button_y = screen.get_height() * 2 // 3
        
        # Store button rect for click detection
        self.restart_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Draw button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        button_color = (0, 150, 0) if self.restart_button_rect.collidepoint(mouse_pos) else (0, 100, 0)
        
        pygame.draw.rect(screen, button_color, self.restart_button_rect)
        pygame.draw.rect(screen, (100, 200, 100), self.restart_button_rect.inflate(-10, -10))
        pygame.draw.rect(screen, (255, 255, 255), self.restart_button_rect, 3)  # White border
        
        # Draw button text
        font = pygame.font.Font(None, 36)
        prompt = font.render("Restart Game", True, (255, 255, 255))
        prompt_rect = prompt.get_rect(center=self.restart_button_rect.center)
        screen.blit(prompt, prompt_rect)
        
        # Additional instructions
        instruction_font = pygame.font.Font(None, 24)
        instruction = instruction_font.render("Click or press ENTER to restart", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(screen.get_width() // 2, button_y + button_height + 20))
        screen.blit(instruction, instruction_rect)
    
    def check_player_health(self):
        """Check if player health has reached 0 and trigger game over."""
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks in the game."""
        # Check if volume slider is being clicked (in any state)
        if hasattr(self, 'volume_slider_rect') and self.volume_slider_rect is not None:
            # Check if the volume handle is clicked
            if hasattr(self, 'volume_handle_rect') and self.volume_handle_rect is not None:
                if self.volume_handle_rect.collidepoint(pos):
                    self.volume_dragging = True
                    return True
                
            # Check if the volume slider track is clicked
            if self.volume_slider_rect.collidepoint(pos):
                # Update volume based on click position
                slider_x = self.volume_slider_rect.x
                slider_width = self.volume_slider_rect.width
                new_volume = max(0, min(1, (pos[0] - slider_x) / slider_width))
                self.music_volume = new_volume
                
                # Update the handle position
                handle_size = self.volume_handle_rect.width
                handle_x = slider_x + int(self.music_volume * slider_width)
                self.volume_handle_rect.x = handle_x - handle_size // 2
                
                # Apply the volume change to the music
                pygame.mixer.music.set_volume(self.music_volume)
                return True
                
        # Handle pause button clicks (check for self.pause_button_rect instead of creating a new rect)
        if self.state in [GameState.WORLD, GameState.BATTLE, GameState.DIALOGUE]:
            # Make sure the pause button rect exists
            if hasattr(self, 'pause_button_rect') and self.pause_button_rect is not None:
                if self.pause_button_rect.collidepoint(pos):
                    # Store the current state and transition to paused
                    print("Pause button clicked, pausing game")
                    self.previous_state = self.state
                    self.state = GameState.PAUSED
                    self.capture_screen_for_pause = True  # Capture the screen for pause background
                    return True
                
        # If in paused state, check for button clicks
        elif self.state == GameState.PAUSED:
            # Check if resume button was clicked
            if hasattr(self, 'resume_button_rect') and self.resume_button_rect is not None:
                if self.resume_button_rect.collidepoint(pos):
                    print("Resume button clicked, resuming game")
                    if hasattr(self, 'previous_state') and self.previous_state is not None:
                        self.state = self.previous_state
                    else:
                        # Default to WORLD state if no previous state exists
                        self.state = GameState.WORLD
                    return True
                
            # Check if main menu button was clicked
            if hasattr(self, 'main_menu_button_rect') and self.main_menu_button_rect is not None:
                if self.main_menu_button_rect.collidepoint(pos):
                    print("Main Menu button clicked, returning to main menu")
                    self.state = GameState.MAIN_MENU
                    return True
                
            # Check if exit button was clicked
            if hasattr(self, 'exit_button_rect') and self.exit_button_rect is not None:
                if self.exit_button_rect.collidepoint(pos):
                    print("Exit button clicked, terminating game")
                    pygame.quit()
                    import sys
                    sys.exit()
                
        # If in game over state, check for restart button click
        elif self.state == GameState.GAME_OVER:
            if hasattr(self, 'restart_button_rect') and self.restart_button_rect is not None:
                if self.restart_button_rect.collidepoint(pos):
                    print("Restart button clicked, restarting game")
                    # Reset player stats
                    self.player.health = self.player.max_health  # Restore full health
                    self.player.skill3_cooldown = 0  # Reset healing cooldown
                    # Start a new game
                    self.setup_new_game()
                    return True
        
        # If in main menu, check for player selection buttons
        elif self.state == GameState.MAIN_MENU:
            # Calculate player selection button positions
            selection_box_width = 400
            selection_box_height = 120
            selection_box_x = (SCREEN_WIDTH - selection_box_width) // 2
            selection_box_y = SCREEN_HEIGHT // 2 - selection_box_height // 2
            
            button_width = 40
            button_spacing = 20
            total_buttons_width = (button_width * self.total_players) + (button_spacing * (self.total_players - 1))
            start_x = selection_box_x + (selection_box_width - total_buttons_width) // 2
            
            # Check if any player button was clicked
            for i in range(1, self.total_players + 1):
                button_x = start_x + (i - 1) * (button_width + button_spacing)
                button_y = selection_box_y + 70
                
                # Calculate button center and distance from click
                button_center_x = button_x + button_width // 2
                button_center_y = button_y + button_width // 2
                
                # Check if click is within button circle
                distance = ((pos[0] - button_center_x) ** 2 + (pos[1] - button_center_y) ** 2) ** 0.5
                if distance <= button_width // 2:
                    # Button clicked, activate selection and set player ID
                    self.player_selection_active = True
                    self.selected_player_id = i
                    return True
            
            # Check if selection box area was clicked to toggle player selection
            if selection_box_x <= pos[0] <= selection_box_x + selection_box_width and \
               selection_box_y <= pos[1] <= selection_box_y + selection_box_height:
                self.player_selection_active = not self.player_selection_active
                return True
                
        return False