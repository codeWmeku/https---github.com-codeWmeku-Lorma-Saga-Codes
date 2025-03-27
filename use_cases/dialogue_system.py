import pygame

class DialogueSystem:
    def __init__(self):
        self.current_dialogue = None
        self.dialogue_lines = []
        self.current_line = 0
        self.font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)
        self.box_color = (0, 0, 0)
        self.box_alpha = 180
        self.padding = 20
        
    def start_dialogue(self, dialogue_lines):
        """Start a new dialogue sequence."""
        self.dialogue_lines = dialogue_lines
        self.current_line = 0
        return self.get_current_dialogue()
    
    def advance_dialogue(self):
        """Advance to the next line of dialogue.
        Returns True if dialogue is finished."""
        self.current_line += 1
        if self.current_line >= len(self.dialogue_lines):
            self.end_dialogue()
            return True
        return False
    
    def get_current_dialogue(self):
        """Get the current dialogue line."""
        if not self.dialogue_lines or self.current_line >= len(self.dialogue_lines):
            return None
        return self.dialogue_lines[self.current_line]
    
    def end_dialogue(self):
        """End the current dialogue sequence."""
        self.dialogue_lines = []
        self.current_line = 0
    
    def render(self, screen):
        """Render the dialogue box and text."""
        if not self.dialogue_lines or self.current_line >= len(self.dialogue_lines):
            return
            
        # Create dialogue box surface
        box_height = 150
        box_surface = pygame.Surface((screen.get_width(), box_height))
        box_surface.fill(self.box_color)
        box_surface.set_alpha(self.box_alpha)
        
        # Position box at bottom of screen
        box_rect = box_surface.get_rect()
        box_rect.bottom = screen.get_height()
        
        # Render text
        text = self.dialogue_lines[self.current_line]
        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = box_rect.centerx
        text_rect.centery = box_rect.centery
        
        # Draw box and text
        screen.blit(box_surface, box_rect)
        screen.blit(text_surface, text_rect)
        
        # Draw prompt indicator
        prompt_text = self.font.render("Press ENTER to continue...", True, self.text_color)
        prompt_rect = prompt_text.get_rect()
        prompt_rect.right = screen.get_width() - self.padding
        prompt_rect.bottom = screen.get_height() - self.padding
        screen.blit(prompt_text, prompt_rect)

    def update(self):
        """Update the dialogue system state."""
        # Currently no state updates are needed per frame
        # This method exists to maintain consistency with other game systems
        pass

    def is_dialogue_finished(self):
        """Check if the dialogue sequence is finished."""
        return not self.dialogue_lines or self.current_line >= len(self.dialogue_lines)