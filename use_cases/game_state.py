from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    WORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    GAME_OVER = auto()
