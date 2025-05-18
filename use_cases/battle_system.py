import random
import pygame
import math

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
        # Use our enhanced battle rendering method
        self.render(screen)

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
        for enemy in self.enemies:
            # Base damage calculation based on attack type
            if attack_type == "basic":
                base_damage = self.player.attack_power
                attack_name = "attacks"
            elif attack_type == "skill":
                base_damage = int(self.player.attack_power * 1.5)
                attack_name = "uses skill on"
            
            # Check for critical hit based on critical chance
            is_critical = False
            damage = base_damage
            if hasattr(self.player, 'critical_chance') and random.randint(1, 100) <= self.player.critical_chance:
                damage = int(damage * 1.5)  # 50% more damage on critical hit
                is_critical = True
            
            # Apply damage to enemy
            enemy.health = max(0, enemy.health - damage)
            
            # Create battle log entry
            if is_critical:
                self.battle_log.append(f"CRITICAL HIT! Player {attack_name} {enemy.name} for {damage} damage!")
            else:
                self.battle_log.append(f"Player {attack_name} {enemy.name} for {damage} damage!")
    
        # Check if all enemies are defeated
        defeated_enemies = [enemy for enemy in self.enemies if enemy.health <= 0]
        if len(defeated_enemies) == len(self.enemies):
            self.battle_log.append(f"All enemies have been defeated!")
            # Award experience points
            exp_gained = sum(25 for _ in self.enemies)  # 25 XP per enemy
            leveled_up = self.player.gain_exp(exp_gained)
            self.battle_log.append(f"Gained {exp_gained} experience!")
            if leveled_up:
                self.battle_log.append(f"Level Up! Player is now level {self.player.level}!")
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
        
    def process_heal(self):
        """Process a healing action from the player."""
        if not hasattr(self.player, 'skill3_heal_amount'):
            self.battle_log.append("Healing skill not available!")
            return None
        
        # Check if healing is on cooldown
        if hasattr(self.player, 'skill3_cooldown') and self.player.skill3_cooldown > 0:
            self.battle_log.append(f"Healing on cooldown: {self.player.skill3_cooldown//60 + 1}s remaining")
            return None
            
        # Calculate healing amount
        heal_amount = self.player.skill3_heal_amount
        
        # Apply healing (ensure it doesn't exceed max health)
        old_health = self.player.health
        self.player.health = min(self.player.max_health, self.player.health + heal_amount)
        actual_heal = self.player.health - old_health
        
        # Set cooldown
        self.player.skill3_cooldown = self.player.skill3_cooldown_max
        
        # Add to battle log
        self.battle_log.append(f"Player used healing! Restored {actual_heal} HP!")
        print(f"Healed player for {actual_heal} HP. Current health: {self.player.health}/{self.player.max_health}")
        
        # Switch turns to enemy
        self.current_turn = "enemy"
        return "heal"
    
    def enemy_turn(self):
        """
        Process enemy turns for multiple enemies.
        
        Returns:
            str: 'defeat' if player is defeated, otherwise None
        """
        for enemy in self.enemies:
            if enemy.health > 0:
                # Check if player dodges the attack based on speed
                dodge_chance = min(5 + (self.player.speed * 2), 30) if hasattr(self.player, 'speed') else 0
                if random.randint(1, 100) <= dodge_chance:
                    # Player dodges the attack
                    self.battle_log.append(f"{enemy.name} attacks but player dodges!")
                    continue
                
                # Calculate base damage
                base_damage = enemy.attack
                
                # Apply player defense if available
                if hasattr(self.player, 'defense'):
                    # Defense reduces damage (minimum 1 damage)
                    reduced_damage = max(1, base_damage - self.player.defense)
                    self.player.health -= reduced_damage
                    self.battle_log.append(f"{enemy.name} attacks player for {reduced_damage} damage! (Reduced by defense)")
                else:
                    # No defense attribute, apply full damage
                    self.player.health -= base_damage
                    self.battle_log.append(f"{enemy.name} attacks player for {base_damage} damage!")
                
                # Check if player is defeated
                if self.player.health <= 0:
                    self.battle_log.append("Player defeated!")
                    return "defeat"
        
        # After all enemies have attacked, switch turn back to player
        self.current_turn = "player"
        self.battle_log.append("Your turn!")
        return None
                
    def update(self):
        """Update battle state, including cooldowns."""
        if not self.battle_active or not self.player:
            return
            
        # Update player cooldowns
        if hasattr(self.player, 'skill3_cooldown') and self.player.skill3_cooldown > 0:
            self.player.skill3_cooldown -= 1
            
        # Process enemy turn if it's their turn
        if self.current_turn == "enemy":
            self.enemy_turn()
    
    def is_battle_over(self):
        """Check if the battle is finished."""
        # Battle is over if player is defeated or all enemies are defeated
        if self.player.health <= 0:
            return True
        
        # Check if all enemies are defeated
        defeated_enemies = [enemy for enemy in self.enemies if enemy.health <= 0]
        return len(defeated_enemies) == len(self.enemies)

    def _draw_battle_background(self, screen):
        """Draw a gradient battle background with decorative elements."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create gradient background from dark blue to black
        for y in range(0, screen_height, 2):  # Draw every other line for performance
            gradient_color = (0, 0, max(0, 50 - y // 10))
            pygame.draw.line(screen, gradient_color, (0, y), (screen_width, y))
        
        # Draw some decorative elements
        for i in range(20):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            radius = random.randint(1, 3)
            alpha = random.randint(50, 150)
            color = (100, 100, 255, alpha)
            star_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, color, (radius, radius), radius)
            screen.blit(star_surface, (x, y))

    def render(self, screen):
        """Render the battle screen with enhanced UI."""
        # Get screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Clear the screen first
        screen.fill((0, 0, 0))
        
        # Draw a styled battle background
        self._draw_battle_background(screen)
        
        # Calculate participant positioning
        num_enemies = len(self.enemies)
        player_x = screen_width // 4
        enemy_base_x = 3 * screen_width // 4
        y = screen_height // 2
        
        # =====================
        # Draw Character UI Panel
        # =====================
        panel_width = 220
        panel_height = 300
        panel_x = 20
        panel_y = 70
        
        # Draw character panel background
        char_panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        char_panel.fill((0, 0, 50, 220))  # Dark blue semi-transparent
        pygame.draw.rect(char_panel, (100, 150, 255), (0, 0, panel_width, panel_height), 2)  # Blue border
        
        # Draw player stats
        font_title = pygame.font.Font(None, 28)
        font_stats = pygame.font.Font(None, 22)
        
        # Character name and icon
        name_text = font_title.render(f"Player {self.player.player_id}", True, (255, 255, 255))
        char_panel.blit(name_text, (10, 10))
        
        # Draw small version of player image
        player_icon = pygame.transform.scale(self.player.image, (50, 50))
        char_panel.blit(player_icon, (panel_width - 60, 10))
        
        # Stats section
        pygame.draw.line(char_panel, (100, 150, 255), (10, 70), (panel_width - 10, 70), 1)
        
        # Hit Points
        hp_text = font_stats.render(f"HP: {self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        char_panel.blit(hp_text, (10, 80))
        
        # Draw HP bar
        hp_bar_width = panel_width - 20
        hp_bar_height = 15
        hp_bar_x = 10
        hp_bar_y = 105
        
        # Background of bar
        pygame.draw.rect(char_panel, (70, 70, 70), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        # Filled portion
        hp_ratio = self.player.health / self.player.max_health
        fill_width = int(hp_bar_width * hp_ratio)
        hp_color = (0, 255, 0) if hp_ratio > 0.5 else ((255, 165, 0) if hp_ratio > 0.25 else (255, 0, 0))
        pygame.draw.rect(char_panel, hp_color, (hp_bar_x, hp_bar_y, fill_width, hp_bar_height))
        
        # Attack Power
        atk_text = font_stats.render(f"Attack: {self.player.attack_power}", True, (255, 255, 255))
        char_panel.blit(atk_text, (10, 130))
        
        # Level and EXP
        level_text = font_stats.render(f"Level: {self.player.level}", True, (255, 255, 255))
        char_panel.blit(level_text, (10, 155))
        
        exp_text = font_stats.render(f"EXP: {self.player.exp}/{self.player.exp_to_next_level}", True, (255, 255, 255))
        char_panel.blit(exp_text, (10, 180))
        
        # Draw EXP bar
        exp_bar_width = panel_width - 20
        exp_bar_height = 10
        exp_bar_x = 10
        exp_bar_y = 200
        
        # Background of bar
        pygame.draw.rect(char_panel, (70, 70, 70), (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height))
        # Filled portion
        exp_ratio = self.player.exp / self.player.exp_to_next_level
        fill_width = int(exp_bar_width * exp_ratio)
        pygame.draw.rect(char_panel, (100, 100, 255), (exp_bar_x, exp_bar_y, fill_width, exp_bar_height))
        
        # Skill cooldown indicator
        if hasattr(self.player, 'skill3_cooldown'):
            skill_cooldown = f"Healing: {'Ready' if self.player.skill3_cooldown <= 0 else f'{self.player.skill3_cooldown}s'}"
            cooldown_color = (0, 255, 0) if self.player.skill3_cooldown <= 0 else (255, 255, 0)
            cooldown_text = font_stats.render(skill_cooldown, True, cooldown_color)
            char_panel.blit(cooldown_text, (10, 220))
        
        # Add panel to screen
        screen.blit(char_panel, (panel_x, panel_y))
        
        # =====================
        # Draw Participants
        # =====================
        # Draw player sprite with subtle animation
        bob_offset = int(math.sin(pygame.time.get_ticks() * 0.005) * 3)
        
        # Create a bright circle behind the player for emphasis
        glow_radius = max(self.player.rect.width, self.player.rect.height) + 20
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (70, 70, 255, 70), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (player_x - glow_radius, y - glow_radius + bob_offset))
        
        # Draw the player sprite at 1.5x size for better visibility
        player_display_width = int(self.player.rect.width * 1.2)
        player_display_height = int(self.player.rect.height * 1.2)
        player_pos = (player_x - player_display_width // 2, y - player_display_height // 2 + bob_offset)
        
        # Scale the player image
        player_image = pygame.transform.scale(self.player.image, (player_display_width, player_display_height))
        screen.blit(player_image, player_pos)
        
        # Draw enemy sprites with spacing proportional to count
        enemy_spacing = min(150, 300 // num_enemies)  # Adjust spacing based on number of enemies
        for i, enemy in enumerate(self.enemies):
            # Create more dynamic positioning for multiple enemies
            if num_enemies == 1:
                enemy_x = enemy_base_x
            else:
                offset = (i - (num_enemies-1)/2) * enemy_spacing
                enemy_x = enemy_base_x + offset
            
            # Add subtle animation for enemies
            enemy_bob = int(math.sin((pygame.time.get_ticks() + i*500) * 0.005) * 3)
            enemy_pos = (enemy_x - enemy.rect.width // 2, y - enemy.rect.height // 2 + enemy_bob)
            
            # Draw enlarged enemy sprite for better visibility
            enlarged_size = (int(enemy.rect.width * 1.5), int(enemy.rect.height * 1.5))
            enlarged_image = pygame.transform.scale(enemy.image, enlarged_size)
            screen.blit(enlarged_image, (enemy_pos[0] - enlarged_size[0]//4, enemy_pos[1] - enlarged_size[1]//4))
            
            # Draw enemy name and health above the sprite
            font = pygame.font.Font(None, 24)
            name_text = font.render(enemy.name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(enemy_x, y - enemy.rect.height - 20))
            screen.blit(name_text, name_rect)
            
            # Draw health bar
            health_ratio = enemy.health / enemy.max_health
            health_width = 80
            health_height = 10
            health_x = enemy_x - health_width // 2
            health_y = y - enemy.rect.height - 10
            
            # Background
            pygame.draw.rect(screen, (70, 70, 70), (health_x, health_y, health_width, health_height))
            # Filled portion
            fill_width = int(health_width * health_ratio)
            health_color = (0, 255, 0) if health_ratio > 0.5 else ((255, 165, 0) if health_ratio > 0.25 else (255, 0, 0))
            pygame.draw.rect(screen, health_color, (health_x, health_y, fill_width, health_height))
        
        # =====================
        # Draw Battle Log
        # =====================
        log_width = 400
        log_height = 120
        log_x = 20
        log_y = screen_height - log_height - 80
        
        # Draw log panel
        log_panel = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
        log_panel.fill((0, 0, 0, 180))  # Semi-transparent black
        pygame.draw.rect(log_panel, (255, 255, 255), (0, 0, log_width, log_height), 1)  # White border
        
        # Draw log title
        font_log_title = pygame.font.Font(None, 24)
        log_title = font_log_title.render("Battle Log", True, (255, 255, 255))
        log_panel.blit(log_title, (log_width//2 - log_title.get_width()//2, 5))
        
        # Draw log entries
        font_log = pygame.font.Font(None, 20)
        entry_y = 30
        for message in self.battle_log[-4:]:  # Show last 4 messages
            log_text = font_log.render(message, True, (255, 255, 255))
            log_panel.blit(log_text, (10, entry_y))
            entry_y += 22
        
        screen.blit(log_panel, (log_x, log_y))
        
        # =====================
        # Draw Battle UI
        # =====================
        # Draw turn indicator at top
        turn_font = pygame.font.Font(None, 36)
        turn_color = (255, 255, 0) if self.current_turn == "player" else (255, 150, 150)
        turn_text = turn_font.render(f"Current Turn: {self.current_turn.title()}", True, turn_color)
        screen.blit(turn_text, (screen_width//2 - turn_text.get_width()//2, 20))
        
        # Draw battle action buttons if it's player's turn
        if self.current_turn == "player":
            self._draw_battle_buttons(screen)
            
    def _draw_battle_background(self, screen):
        """Draw an enhanced battle background."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create a gradient background
        background = pygame.Surface((screen_width, screen_height))
        for y in range(screen_height):
            # Create a dark blue to black gradient
            color_value = max(0, 30 - y * 30 // screen_height)
            background.fill((0, 0, color_value), (0, y, screen_width, 1))
        
        screen.blit(background, (0, 0))
        
        # Draw some decorative lines
        for i in range(10):
            start_y = random.randint(0, screen_height)
            end_y = random.randint(0, screen_height)
            pygame.draw.line(screen, (0, 0, 50), (0, start_y), (screen_width, end_y), 1)
            
    def _draw_battle_buttons(self, screen):
        """Draw stylized battle action buttons."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Button dimensions
        button_width = 200
        button_height = 50
        button_spacing = 20
        button_y = screen_height - button_height - 20
        
        # Mouse position for hover effects
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Create buttons
        buttons = [
            {"text": "Basic Attack", "key": "1", "x": screen_width//2 - button_width - button_spacing//2},
            {"text": "Skill Attack", "key": "2", "x": screen_width//2 + button_spacing//2},
            {"text": "Heal", "key": "3", "x": screen_width//2 + button_width + button_spacing + button_spacing//2}
        ]
        
        for button in buttons:
            button_rect = pygame.Rect(button["x"], button_y, button_width, button_height)
            hover = button_rect.collidepoint(mouse_x, mouse_y)
            
            # Button background
            color = (80, 80, 180) if hover else (50, 50, 150)
            pygame.draw.rect(screen, color, button_rect, border_radius=10)
            pygame.draw.rect(screen, (150, 150, 255), button_rect, 2, border_radius=10)
            
            # Button text
            font = pygame.font.Font(None, 26)
            key_text = font.render(f"[{button['key']}]", True, (200, 200, 255))
            button_text = font.render(button["text"], True, (255, 255, 255))
            
            # Position text
            screen.blit(key_text, (button_rect.x + 10, button_rect.y + button_height//2 - key_text.get_height()//2))
            screen.blit(button_text, (button_rect.x + 40, button_rect.y + button_height//2 - button_text.get_height()//2))