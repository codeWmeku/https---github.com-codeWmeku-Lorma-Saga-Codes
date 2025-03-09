import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from use_cases.battle_system import BattleSystem
from use_cases.dialogue_system import DialogueSystem
from use_cases.game_logic import GameLogic
from interface_adapters.controllers.input_controller import InputController
from interface_adapters.controllers.game_controller import GameController

class PygameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Lorma Saga")
        self.clock = pygame.time.Clock()
        
        # Set up game components
        self.battle_system = BattleSystem()
        self.dialogue_system = DialogueSystem()
        self.game_logic = GameLogic(self.battle_system, self.dialogue_system)
        self.input_controller = InputController(self.game_logic)
        self.game_controller = GameController(self.screen, self.game_logic)
    
    def run(self):
        running = True
        
        while running:
            # Process input
            running = self.input_controller.process_input()
            
            # Update game state
            self.game_controller.update()
            
            # Render
            self.game_controller.render()
            
            # Cap the framerate
            self.clock.tick(FPS)
        
        pygame.quit()