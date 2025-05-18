# config.py
import pygame
from enum import Enum

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60
MAP_WIDTH = 2000
MAP_HEIGHT = 2000

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game states
class GameState(Enum):
    MAIN_MENU = 0
    WORLD = 1
    BATTLE = 2
    DIALOGUE = 3
    GAME_OVER = 4
    VICTORY = 5
    PAUSED = 6
