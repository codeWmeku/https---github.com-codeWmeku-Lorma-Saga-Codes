# main.py
import pygame
import sys
from interface_adapters.controllers.input_controller import InputController
from use_cases.game_logic import GameLogic

def main():
    # Initialize Pygame
    pygame.init()
    
    # Initialize the mixer for audio
    pygame.mixer.init()
    
    # Set up the display in fullscreen mode
    info = pygame.display.Info()
    SCREEN_WIDTH = info.current_w
    SCREEN_HEIGHT = info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Lorma Saga")
    
    # Enable key repeat for better control
    pygame.key.set_repeat(200, 50)  # Delay, interval in milliseconds
    
    # Initialize game systems
    game_logic = GameLogic()  # GameLogic now creates its own battle and dialogue systems
    input_controller = InputController(game_logic)
    
    # Load and play background music
    try:
        pygame.mixer.music.load('assets/game_music/game bg music.mp3')
        pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        print("Background music loaded and playing")
    except Exception as e:
        print(f"Error loading background music: {e}")
    
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