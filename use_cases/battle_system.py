import random
import pygame

class BattleSystem:
    def __init__(self, screen_width=800, screen_height=600, map_width=1600, map_height=1200):
        self.current_turn = "player"
        self.battle_log = []
        self.turn_counter = 0
        self.player = None
        self.enemies = []  
        self.battle_active = False
        
        # Battle UI elements
        self.font = pygame.font.Font(None, 32)
        self.battle_bg_color = (50, 50, 50)
        self.text_color = (255, 255, 255)

    def start_battle(self, player, enemies):
        """
        Start battle with player and multiple enemies.
        
        Args:
            player: Player character
            enemies: Single enemy or list of enemies
        """
        self.player = player
        
        # Ensure enemies is always a list
        self.enemies = [enemies] if not isinstance(enemies, list) else enemies
        
        # Determine first turn based on highest speed
        speeds = [enemy.speed for enemy in self.enemies]
        self.current_turn = "player" if player.speed > max(speeds) else "enemy"
        
        self.battle_log = [f"Battle with {', '.join(enemy.name for enemy in self.enemies)} has begun!"]
        self.battle_active = True

    def draw(self, screen):
        """Render the battle screen."""
        # Fill screen with battle background
        screen.fill(self.battle_bg_color)
        
        # Render player and enemy stats
        if self.player and self.enemies:
            # Player stats
            player_text = f"Player HP: {self.player.health}/{self.player.max_health}"
            player_surface = self.font.render(player_text, True, self.text_color)
            screen.blit(player_surface, (50, 50))
            
            # Draw player health bar
            self._draw_health_bar(screen, self.player, screen.get_width() // 4, screen.get_height() // 3)
            
            # Enemy stats and health bars
            for i, enemy in enumerate(self.enemies):
                enemy_text = f"{enemy.name} HP: {enemy.health}/{enemy.max_health}"
                enemy_surface = self.font.render(enemy_text, True, self.text_color)
                screen.blit(enemy_surface, (screen.get_width() - 300, 50 + i * 40))
                
                # Draw enemy health bar
                self._draw_health_bar(screen, enemy, screen.get_width() * 3 // 4, screen.get_height() // 3 + i * 50)
            
            # Battle log
            log_y = 250  
            for log_entry in self.battle_log[-5:]:  # Show last 5 log entries
                log_surface = self.font.render(log_entry, True, self.text_color)
                screen.blit(log_surface, (50, log_y))
                log_y += 40
            
            # Current turn indicator
            turn_text = f"Current Turn: {self.current_turn.capitalize()}"
            turn_surface = self.font.render(turn_text, True, self.text_color)
            screen.blit(turn_surface, (screen.get_width() // 2 - 100, screen.get_height() - 150))

            # Attack turn options
            if self.current_turn == "player":
                options_text = self.font.render("1: Basic Attack    2: Skill", True, (255, 255, 255))
                screen.blit(options_text, (20, screen.get_height() - 100))
            
            # Render the rest of the screen
            # ... (rest of the method remains the same)

    def _draw_health_bar(self, screen, entity, x, y):
        """Draw a health bar for the given entity."""
        # Ensure we have a valid screen and entity
        if not screen or not entity:
            return
        
        bar_width = 200
        bar_height = 20
        bar_x = x - bar_width // 2
        
        # Ensure health values are valid
        if not hasattr(entity, 'health') or not hasattr(entity, 'max_health'):
            return
        
        # Prevent division by zero and negative health
        max_health = max(1, entity.max_health)
        current_health = max(0, entity.health)
        
        # Draw background (dark red)
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, y, bar_width, bar_height))
        
        # Draw filled portion (bright green)
        health_ratio = current_health / max_health
        fill_width = int(bar_width * health_ratio)
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, y, fill_width, bar_height))
        
        # Draw border (white)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, y, bar_width, bar_height), 3)
        
        # Draw name above health bar
        font = pygame.font.Font(None, 24)
        if hasattr(entity, 'name'):
            name_text = font.render(str(entity.name), True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(x, y - 10))
            screen.blit(name_text, name_rect)

    def player_attack(self, attack_type):
        if attack_type == "basic":
            damage = self.player.attack_power
            for enemy in self.enemies:
                enemy.health = max(0, enemy.health - damage)
                self.battle_log.append(f"Player attacks {enemy.name} for {damage} damage!")
        elif attack_type == "skill":
            damage = self.player.attack_power * 1.5
            for enemy in self.enemies:
                enemy.health = max(0, enemy.health - damage)
                self.battle_log.append(f"Player uses skill on {enemy.name} for {damage} damage!")
        
        # Check if all enemies are defeated
        defeated_enemies = [enemy for enemy in self.enemies if enemy.health <= 0]
        if len(defeated_enemies) == len(self.enemies):
            self.battle_log.append(f"All enemies have been defeated!")
            self.player.exp += sum(enemy.exp for enemy in self.enemies)
            self.battle_log.append(f"Gained {sum(enemy.exp for enemy in self.enemies)} experience!")
            return "victory"
        
        self.current_turn = "enemy"
        return None

    def process_attack(self, player):
        """Process a basic attack from the player."""
        result = self.player_attack("basic")
        return result

    def process_skill(self, player):
        """Process a skill attack from the player."""
        result = self.player_attack("skill")
        return result

    def enemy_turn(self):
        """
        Process enemy turns for multiple enemies.
        
        Returns:
            str: 'defeat' if player is defeated, otherwise None
        """
        for enemy in self.enemies:
            if enemy.health > 0:
                # Basic enemy AI: attack player
                damage = enemy.attack
                self.player.health -= damage
                self.battle_log.append(f"{enemy.name} attacks player for {damage} damage!")
                
                # Check if player is defeated
                if self.player.health <= 0:
                    self.battle_log.append("Player defeated!")
                    return "defeat"
        
        # Switch turn back to player
        self.current_turn = "player"
        return None

    def update(self):
        """Update battle state."""
        if not self.battle_active:
            return
            
        # If it's enemy's turn, process it automatically
        if self.current_turn == "enemy":
            result = self.enemy_turn()
            if result == "defeat":
                self.battle_active = False
    
    def is_battle_over(self):
        """Check if the battle is finished."""
        # Battle is over if player is defeated or all enemies are defeated
        if self.player.health <= 0:
            return True
        
        # Check if all enemies are defeated
        defeated_enemies = [enemy for enemy in self.enemies if enemy.health <= 0]
        return len(defeated_enemies) == len(self.enemies)

    def render(self, screen):
        """Render the battle screen."""
        # Draw background
        screen.fill((0, 0, 0))  # Black background
        
        # Calculate enemy positioning
        num_enemies = len(self.enemies)
        screen_width = screen.get_width()
        
        # Draw battle participants
        player_x = screen_width // (num_enemies + 1)
        y = screen.get_height() // 2
        
        # Draw player sprite
        screen.blit(self.player.image, (player_x - self.player.rect.width // 2, y - self.player.rect.height // 2))
        
        # Draw enemy sprites
        for i, enemy in enumerate(self.enemies, 1):
            enemy_x = (i + 1) * screen_width // (num_enemies + 1)
            screen.blit(enemy.image, (enemy_x - enemy.rect.width // 2, y - enemy.rect.height // 2))
        
        # Draw health bars
        self._draw_health_bar(screen, self.player, player_x, screen.get_height() // 3)
        
        # Draw enemy health bars
        for i, enemy in enumerate(self.enemies, 1):
            enemy_x = (i + 1) * screen_width // (num_enemies + 1)
            self._draw_health_bar(screen, enemy, enemy_x, screen.get_height() // 3 + i * 50)
        
        # Draw battle log (last 3 messages)
        font = pygame.font.Font(None, 36)
        log_y = screen.get_height() - 150
        for message in self.battle_log[-3:]:
            text = font.render(message, True, (255, 255, 255))
            screen.blit(text, (20, log_y))
            log_y += 30
        
        # Draw turn indicator
        turn_text = font.render(f"Current Turn: {self.current_turn.title()}", True, (255, 255, 0))
        screen.blit(turn_text, (20, 20))
        
        # Draw battle options if it's player's turn
        if self.current_turn == "player":
            options_text = font.render("1: Basic Attack    2: Skill", True, (255, 255, 255))
            screen.blit(options_text, (20, screen.get_height() - 40))