import pygame
import os
from settings import *

class Zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 0.15
        self.health = 100
        self.is_attacking = False
        self.last_hit_time = 0
        
        image_path = os.path.join("assets", "zombie.png")
        self.base_image = pygame.image.load(image_path).convert_alpha()
        
    def update(self, player):
        if self.scale < MAX_ZOMBIE_SCALE:
            self.scale += ZOMBIE_GROWTH_RATE
        else:
            self.is_attacking = True
            player.health -= 0.5 
            
    def draw(self, surface):
        new_width = int(self.base_image.get_width() * self.scale)
        new_height = int(self.base_image.get_height() * self.scale)
        
        scaled_image = pygame.transform.scale(self.base_image, (new_width, new_height))
        rect = scaled_image.get_rect(midbottom=(self.x, self.y))
        surface.blit(scaled_image, rect)
        
        if pygame.time.get_ticks() - self.last_hit_time < 150:
            flash_surf = scaled_image.copy()
            flash_surf.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_surf, rect)
        
    def check_shot(self, mouse_pos, damage):
        new_width = int(self.base_image.get_width() * self.scale)
        new_height = int(self.base_image.get_height() * self.scale)
        
        rect = pygame.Rect(0, 0, new_width, new_height)
        rect.midbottom = (self.x, self.y)
        
        if rect.collidepoint(mouse_pos):
            self.health -= damage
            self.last_hit_time = pygame.time.get_ticks()
            return True
        return False