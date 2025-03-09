class DialogueSystem:
    def __init__(self):
        self.current_npc = None
        self.dialogue_index = 0
        
    def start_dialogue(self, npc):
        self.current_npc = npc
        self.dialogue_index = 0
        return self.get_current_dialogue()
    
    def get_current_dialogue(self):
        if not self.current_npc or self.dialogue_index >= len(self.current_npc.dialogue):
            return None
        
        return {
            "name": self.current_npc.name,
            "text": self.current_npc.dialogue[self.dialogue_index]
        }
    
    def next_dialogue(self):
        self.dialogue_index += 1
        return self.get_current_dialogue()
    
    def end_dialogue(self):
        self.current_npc = None
        self.dialogue_index = 0