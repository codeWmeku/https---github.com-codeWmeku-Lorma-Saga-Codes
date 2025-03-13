# game_logic.py
import pygame
import random
from config import GameState, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from entities.player import Player
from entities.enemy import Enemy, GrandMaster
from entities.npc import NPC
from entities.wall import Wall

class GameLogic:
    def __init__(self, battle_system, dialogue_system):
        self.battle_system = battle_system
        self.dialogue_system = dialogue_system
        self.state = GameState.MAIN_MENU
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.player = None
        
    def setup_new_game(self):
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.player)
        
        # Clear existing entities
        self.walls.empty()
        self.enemies.empty()
        self.npcs.empty()
        
        # Create some walls
        for i in range(10):
            wall = Wall(random.randint(0, MAP_WIDTH - 100), 
                       random.randint(0, MAP_HEIGHT - 100), 
                       TILE_SIZE, TILE_SIZE)
            self.walls.add(wall)
            self.all_sprites.add(wall)
        
        # Create some enemies
        for i in range(5):
            enemy = Enemy(random.randint(100, MAP_WIDTH - 100),
                         random.randint(100, MAP_HEIGHT - 100),
                         "Orc", 50, 10, 25)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Create an NPC
        npc = NPC(300, 300, "Classmate", ["Hey there! Welcome to Lorma School!", 
                                          "Watch out for the Grandmasters!", 
                                          "Good luck on your journey!"])
        self.npcs.add(npc)
        self.all_sprites.add(npc)
        
        # Create the final boss
        self.final_boss = GrandMaster(MAP_WIDTH - 200, MAP_HEIGHT - 200,
                                     "Grandmaster Mary-Ann", 300, 20, 500,
                                     [
                                         {"name": "Late Penalty", "damage": 15, "effect": "Speed decreased"},
                                         {"name": "Dark Magic", "damage": 25, "effect": "Critical hit!"},
                                         {"name": "Harsh Grading", "damage": 20, "effect": "Attack decreased"}
                                     ])
        self.enemies.add(self.final_boss)
        self.all_sprites.add(self.final_boss)
        
        self.state = GameState.WORLD
        
    def check_enemy_collision(self):
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if enemy_hits:
            enemy = enemy_hits[0]
            self.battle_system.start_battle(self.player, enemy)
            self.state = GameState.BATTLE
    
    def check_npc_interaction(self):
        for npc in self.npcs:
            dx = npc.rect.x - self.player.rect.x
            dy = npc.rect.y - self.player.rect.y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < npc.interaction_range:
                self.dialogue_system.start_dialogue(npc)
                self.state = GameState.DIALOGUE
                break
    
    def update_world(self, dx, dy):
        self.player.move(dx, dy, self.walls)
        
        for enemy in self.enemies:
            enemy.update(self.player)
        
        self.check_enemy_collision()
    
    def handle_battle_input(self, action):
        result = None
        
        if self.battle_system.current_turn == "player":
            if action == "basic_attack":
                result = self.battle_system.player_attack("basic")
            elif action == "skill":
                result = self.battle_system.player_attack("skill")
            
            if result is None and self.battle_system.current_turn == "enemy":
                enemy_result = self.battle_system.enemy_turn()
                if enemy_result:
                    result = enemy_result
        
        if result == "victory":
            self.enemies.remove(self.battle_system.enemy)
            self.all_sprites.remove(self.battle_system.enemy)
            self.state = GameState.WORLD
        elif result == "game_over":
            self.state = GameState.GAME_OVER
        
        return result
    
    def handle_dialogue_input(self):
        next_dialogue = self.dialogue_system.next_dialogue()
        if not next_dialogue:
            self.dialogue_system.end_dialogue()
            self.state = GameState.WORLD