from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    WORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    GAME_OVER = auto()
    PAUSED = auto()
    SKIPPED = auto()

    def __str__(self):
        return self.name.lower()
