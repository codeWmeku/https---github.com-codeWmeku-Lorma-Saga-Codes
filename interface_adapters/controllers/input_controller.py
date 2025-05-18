import pygame
from config import GameState

class InputController:
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.key_config = {
            'move_left': [pygame.K_LEFT, pygame.K_a],
            'move_right': [pygame.K_RIGHT, pygame.K_d],
            'move_up': [pygame.K_UP, pygame.K_w],
            'move_down': [pygame.K_DOWN, pygame.K_s],
            'interact': [pygame.K_e],
            'attack': [pygame.K_SPACE],
            'pause': [pygame.K_ESCAPE],
            'confirm': [pygame.K_RETURN],
            'battle_basic': [pygame.K_1],
            'battle_skill': [pygame.K_2],
            'battle_heal': [pygame.K_3]
        }
        # Track movement keys
        self.movement_keys_pressed = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }
    
    def process_input(self):
        dx = 0
        dy = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Handle movement key presses
                if event.key in self.key_config['move_left']:
                    self.movement_keys_pressed['left'] = True
                elif event.key in self.key_config['move_right']:
                    self.movement_keys_pressed['right'] = True
                elif event.key in self.key_config['move_up']:
                    self.movement_keys_pressed['up'] = True
                elif event.key in self.key_config['move_down']:
                    self.movement_keys_pressed['down'] = True
                
                # Handle player selection in main menu
                if self.game_logic.state == GameState.MAIN_MENU:
                    if event.key == pygame.K_UP:
                        # Toggle player selection mode
                        self.game_logic.player_selection_active = not self.game_logic.player_selection_active
                        print(f"Player selection mode: {'Active' if self.game_logic.player_selection_active else 'Inactive'}")
                    elif event.key == pygame.K_LEFT and self.game_logic.player_selection_active:
                        # Decrease player ID (with wraparound)
                        self.game_logic.selected_player_id = ((self.game_logic.selected_player_id - 2) % self.game_logic.total_players) + 1
                        print(f"Selected Player ID: {self.game_logic.selected_player_id}")
                    elif event.key == pygame.K_RIGHT and self.game_logic.player_selection_active:
                        # Increase player ID (with wraparound)
                        self.game_logic.selected_player_id = (self.game_logic.selected_player_id % self.game_logic.total_players) + 1
                        print(f"Selected Player ID: {self.game_logic.selected_player_id}")
                
                # Handle other key presses
                if event.key in self.key_config['confirm']:
                    if self.game_logic.state == GameState.MAIN_MENU:
                        self.game_logic.setup_new_game()
                    elif self.game_logic.state == GameState.DIALOGUE:
                        self.game_logic.handle_dialogue_input()
                    elif self.game_logic.state == GameState.GAME_OVER:
                        self.game_logic.setup_new_game()
                        
                elif event.key in self.key_config['interact'] and self.game_logic.state == GameState.WORLD:
                    self.game_logic.handle_interaction()
                    
                elif event.key in self.key_config['pause']:
                    # Handle pause functionality based on current state
                    if self.game_logic.state == GameState.WORLD or self.game_logic.state == GameState.BATTLE or self.game_logic.state == GameState.DIALOGUE:
                        # If in a gameplay state, transition to pause
                        self.game_logic.previous_state = self.game_logic.state
                        self.game_logic.state = GameState.PAUSED
                        self.game_logic.capture_screen_for_pause = True
                    elif self.game_logic.state == GameState.PAUSED:
                        # If already paused, resume previous state
                        if hasattr(self.game_logic, 'previous_state') and self.game_logic.previous_state is not None:
                            self.game_logic.state = self.game_logic.previous_state
                        else:
                            # Default to world if no previous state
                            self.game_logic.state = GameState.WORLD
                
                # Add exit handling with Escape key while holding Alt
                elif event.key == pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_ALT:
                    print("Alt+ESC pressed, exiting game")
                    return False
                
                # Pause functionality is now handled in game_logic.handle_key_event
                        
                elif self.game_logic.state == GameState.BATTLE:
                    if event.key in self.key_config['battle_basic']:
                        self.game_logic.handle_battle_input("basic_attack")
                    elif event.key in self.key_config['battle_skill']:
                        self.game_logic.handle_battle_input("skill")
                    elif event.key in self.key_config['battle_heal']:
                        self.game_logic.handle_battle_input("heal")
            
            elif event.type == pygame.KEYUP:
                # Handle movement key releases
                if event.key in self.key_config['move_left']:
                    self.movement_keys_pressed['left'] = False
                elif event.key in self.key_config['move_right']:
                    self.movement_keys_pressed['right'] = False
                elif event.key in self.key_config['move_up']:
                    self.movement_keys_pressed['up'] = False
                elif event.key in self.key_config['move_down']:
                    self.movement_keys_pressed['down'] = False
            
            # Mouse click handling for attacks and UI interactions
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # First check if the mouse click is handled by the game logic (UI elements, etc.)
                    if self.game_logic.handle_mouse_click(event.pos):
                        pass  # Click was handled by UI
                    # Otherwise, handle gameplay clicks
                    elif self.game_logic.state == GameState.WORLD:
                        self.game_logic.handle_attack()
                    elif self.game_logic.state == GameState.BATTLE:
                        self.game_logic.handle_battle_input("basic_attack")
        
        # Calculate movement based on currently pressed keys
        if self.game_logic.state == GameState.WORLD:
            # Determine movement direction
            if self.movement_keys_pressed['left']:
                dx = -1
            if self.movement_keys_pressed['right']:
                dx = 1
            if self.movement_keys_pressed['up']:
                dy = -1
            if self.movement_keys_pressed['down']:
                dy = 1
            
            # Update player movement
            self.game_logic.handle_movement(dx, dy)
        
        return True