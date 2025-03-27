# main.py
import pygame
import sys
from interface_adapters.controllers.input_controller import InputController
from use_cases.game_logic import GameLogic

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lorma Saga")
    
    # Initialize game systems
    game_logic = GameLogic()  # GameLogic now creates its own battle and dialogue systems
    input_controller = InputController(game_logic)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Process input
        running = input_controller.process_input()
        
        # Update game state
        game_logic.update()
        
        # Render
        game_logic.render(screen)
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()