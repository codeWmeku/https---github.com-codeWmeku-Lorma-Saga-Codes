# game_controller.py
import pygame
from config import BLACK, GameState, SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, WHITE, RED, GREEN
from interface_adapters.views.renderer import Camera, Renderer
from interface_adapters.views.ui_elements import Button

class GameController:
    def __init__(self, screen, game_logic):
        self.screen = screen
        self.game_logic = game_logic
        self.renderer = Renderer(screen)
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # UI elements
        self.start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2,
                              200, 50, "Start Game", WHITE, GREEN)
        
        # Add gameplay instructions
        self.instructions = [
            "Move: WASD or Arrow Keys",
            "Attack: Space or Left Mouse Button",
            "Interact with NPCs: E Key",
            "In Battle: 1 for Basic Attack, 2 for Skill"
        ]
        
    def update(self):
        if self.game_logic.state == GameState.WORLD and self.game_logic.player:
            self.camera.update(self.game_logic.player)
            
        if self.game_logic.state == GameState.MAIN_MENU:
            self.start_button.update()
            if self.start_button.is_clicked():
                self.game_logic.setup_new_game()
                
    def render(self):
        self.renderer.clear_screen()
        
        if self.game_logic.state == GameState.MAIN_MENU:
            self.renderer.draw_text("LORMA SAGA", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 4, RED)
            self.start_button.draw(self.screen)
            
            # Draw instructions
            for i, instruction in enumerate(self.instructions):
                self.renderer.draw_text(instruction, SCREEN_WIDTH // 2 - 150, 
                                        SCREEN_HEIGHT // 2 + 80 + i * 30)
            
        elif self.game_logic.state == GameState.WORLD:
            # Draw all sprites with camera offset
            self.renderer.draw_sprite_group(self.game_logic.all_sprites, self.camera)
            
            # Draw player stats
            player = self.game_logic.player
            self.renderer.draw_health_bar(10, 10, 200, 20, player.hp, player.max_hp, RED)
            self.renderer.draw_text(f"HP: {player.hp}/{player.max_hp}", 220, 10)
            self.renderer.draw_text(f"Level: {player.level}", 10, 40)
            self.renderer.draw_text(f"EXP: {player.exp}/{player.next_level_exp}", 10, 70)
            
            # Display controls
            self.renderer.draw_text("SPACE to Attack", 10, SCREEN_HEIGHT - 30)
            
        elif self.game_logic.state == GameState.BATTLE:
            battle = self.game_logic.battle_system
            player = battle.player
            enemy = battle.enemy
            
            # Draw battle interface
            self.renderer.draw_text(f"Battle: {player.name} vs {enemy.name}", 
                               SCREEN_WIDTH // 2 - 150, 20)
            
            # Draw player stats
            self.renderer.draw_health_bar(50, 100, 200, 20, player.hp, player.max_hp, GREEN)
            self.renderer.draw_text(f"{player.name}: {player.hp}/{player.max_hp} HP", 50, 130)
            
            # Draw enemy stats
            self.renderer.draw_health_bar(SCREEN_WIDTH - 250, 100, 200, 20, 
                                     enemy.hp, enemy.max_hp, RED)
            self.renderer.draw_text(f"{enemy.name}: {enemy.hp}/{enemy.max_hp} HP", 
                               SCREEN_WIDTH - 250, 130)
            
            # Draw battle log
            y_offset = 200
            for i, log in enumerate(battle.battle_log[-5:]):
                self.renderer.draw_text(log, 50, y_offset + i * 30)
            
            # Draw actions
            self.renderer.draw_text("1: Basic Attack", 50, SCREEN_HEIGHT - 100)
            self.renderer.draw_text("2: Skill Attack", 50, SCREEN_HEIGHT - 70)
            
            if battle.current_turn == "player":
                self.renderer.draw_text("Your turn!", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 40)
            else:
                self.renderer.draw_text("Enemy turn...", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 40)
            
        elif self.game_logic.state == GameState.DIALOGUE:
            dialogue = self.game_logic.dialogue_system.get_current_dialogue()
            if dialogue:
                # Draw dialogue box
                pygame.draw.rect(self.screen, WHITE, (50, SCREEN_HEIGHT - 150, 
                                                 SCREEN_WIDTH - 100, 120))
                pygame.draw.rect(self.screen, BLACK, (50, SCREEN_HEIGHT - 150, 
                                                 SCREEN_WIDTH - 100, 120), 2)
                
                self.renderer.draw_text(f"{dialogue['name']}:", 60, SCREEN_HEIGHT - 140)
                self.renderer.draw_text(dialogue['text'], 60, SCREEN_HEIGHT - 110)
                self.renderer.draw_text("Press ENTER to continue...", 
                                   SCREEN_WIDTH - 250, SCREEN_HEIGHT - 50)
            
        elif self.game_logic.state == GameState.GAME_OVER:
            self.renderer.draw_text("GAME OVER", SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20, RED)
            self.renderer.draw_text("Press ENTER to return to main menu", 
                               SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 20)
                               
        elif self.game_logic.state == GameState.VICTORY:
            self.renderer.draw_text("VICTORY!", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 40, GREEN)
            self.renderer.draw_text("You defeated the Grandmaster!", 
                               SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2)
            self.renderer.draw_text("Press ENTER to return to main menu", 
                               SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 40)
            
        pygame.display.flip()