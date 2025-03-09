import pygame
from config import GameState

class InputController:
    def __init__(self, game_logic):
        self.game_logic = game_logic
        
    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Mouse click handling
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if self.game_logic.state == GameState.WORLD:
                        # Trigger attack animation in world mode
                        self.game_logic.player.attack_action()
                    elif self.game_logic.state == GameState.BATTLE:
                        # Use attack in battle mode
                        self.game_logic.handle_battle_input("basic_attack")
                
            if self.game_logic.state == GameState.MAIN_MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.game_logic.setup_new_game()
                    
            elif self.game_logic.state == GameState.BATTLE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.game_logic.handle_battle_input("basic_attack")
                    elif event.key == pygame.K_2:
                        self.game_logic.handle_battle_input("skill")
                    
            elif self.game_logic.state == GameState.DIALOGUE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.game_logic.handle_dialogue_input()
                    
            elif self.game_logic.state in [GameState.GAME_OVER, GameState.VICTORY]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.game_logic.state = GameState.MAIN_MENU
            
        # Continuous input for player movement and attacks
        if self.game_logic.state == GameState.WORLD:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            # Support both WASD and arrow keys
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            
            if dx != 0 or dy != 0:
                self.game_logic.update_world(dx, dy)
                
            # Attack with space key
            if keys[pygame.K_SPACE]:
                self.game_logic.player.attack_action()
                
            # Check for NPC interaction with E key
            if keys[pygame.K_e]:
                self.game_logic.check_npc_interaction()
                
        return True