import random
import pygame

class BattleSystem:
    def __init__(self):
        self.player = None
        self.enemy = None
        self.current_turn = None
        self.battle_log = []
        self.turn_count = 0
        
    def start_battle(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.current_turn = "player"  # Player goes first
        self.battle_log = []
        self.turn_count = 0
        self.add_to_log(f"Battle started! {player.name} vs {enemy.name}")
        
    def add_to_log(self, message):
        self.battle_log.append(message)
        # Keep log from getting too long
        if len(self.battle_log) > 10:
            self.battle_log.pop(0)
            
    def player_attack(self, attack_type):
        if self.current_turn != "player":
            return None
            
        damage = 0
        if attack_type == "basic":
            damage = self.player.basic_attack()
            self.add_to_log(f"{self.player.name} used Basic Attack for {damage} damage!")
        elif attack_type == "skill":
            damage = self.player.use_skill()
            self.add_to_log(f"{self.player.name} used Skill Attack for {damage} damage!")
            
        # Apply damage to enemy
        is_defeated = self.enemy.take_damage(damage)
        
        # Check if enemy is defeated
        if is_defeated:
            self.add_to_log(f"{self.enemy.name} was defeated!")
            # Award experience to player
            level_up_msg = self.player.gain_exp(self.enemy.exp_reward)
            if level_up_msg:
                self.add_to_log(level_up_msg)
            return "victory"
            
        # Switch turns
        self.current_turn = "enemy"
        return None
        
    def enemy_turn(self):
        if self.current_turn != "enemy":
            return None
            
        # For basic enemies
        if not hasattr(self.enemy, 'use_skill'):
            damage = self.enemy.attack
            self.add_to_log(f"{self.enemy.name} attacks for {damage} damage!")
        else:
            # For boss enemies with skills
            skill = self.enemy.use_skill()
            damage = skill.get("damage", self.enemy.attack)
            effect = skill.get("effect", "")
            self.add_to_log(f"{self.enemy.name} used {skill['name']} for {damage} damage! {effect}")
            
        # Apply damage to player
        self.player.hp = max(0, self.player.hp - damage)
        
        # Check if player is defeated
        if self.player.hp <= 0:
            self.add_to_log(f"{self.player.name} was defeated!")
            return "game_over"
            
        # Switch turns
        self.current_turn = "player"
        self.turn_count += 1
        return None