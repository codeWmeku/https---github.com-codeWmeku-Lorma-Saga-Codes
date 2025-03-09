import random

class BattleSystem:
    def __init__(self):
        self.current_turn = "player"
        self.battle_log = []
        self.turn_counter = 0
    
    def start_battle(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.current_turn = "player" if player.speed > enemy.speed else "enemy"
        self.battle_log = [f"Battle with {enemy.name} has begun!"]
        self.turn_counter = 0
        
    def player_attack(self, attack_type):
        if attack_type == "basic":
            damage = self.player.basic_attack()
            self.enemy.hp = max(0, self.enemy.hp - damage)
            self.battle_log.append(f"{self.player.name} attacks for {damage} damage!")
        elif attack_type == "skill":
            damage = self.player.use_skill()
            self.enemy.hp = max(0, self.enemy.hp - damage)
            self.battle_log.append(f"{self.player.name} uses skill for {damage} damage!")
        
        if self.enemy.hp <= 0:
            self.battle_log.append(f"{self.enemy.name} has been defeated!")
            level_up_msg = self.player.gain_exp(self.enemy.exp_reward)
            self.battle_log.append(f"Gained {self.enemy.exp_reward} experience!")
            if level_up_msg:
                self.battle_log.append(level_up_msg)
            return "victory"
        
        self.current_turn = "enemy"
        return None
    
    def enemy_turn(self):
        if hasattr(self.enemy, "use_skill") and random.random() < 0.3:
            skill = self.enemy.use_skill()
            damage = skill["damage"]
            self.player.hp = max(0, self.player.hp - damage)
            self.battle_log.append(f"{self.enemy.name} uses {skill['name']} for {damage} damage!")
            if "effect" in skill and skill["effect"]:
                self.battle_log.append(f"Effect: {skill['effect']}")
        else:
            damage = self.enemy.attack
            self.player.hp = max(0, self.player.hp - damage)
            self.battle_log.append(f"{self.enemy.name} attacks for {damage} damage!")
        
        if self.player.hp <= 0:
            self.battle_log.append(f"{self.player.name} has been defeated!")
            return "game_over"
        
        self.current_turn = "player"
        self.turn_counter += 1
        return None