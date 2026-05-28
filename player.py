import pygame
import os
from settings import *

class Player:
    def __init__(self):
        self.health = 100
        self.gun_damage = 50
        
        # Ammo System
        self.ammo = 30
        self.max_ammo = 30
        self.is_reloading = False
        self.reload_start_time = 0
        self.reload_duration = 1500  # 1.5 seconds to reload
        
        pygame.mixer.init()
        sound_path = os.path.join("assets", "shoot.wav")
        self.shoot_sound = pygame.mixer.Sound(sound_path)
        self.shoot_sound.set_volume(0.5)
        
        gun_path = os.path.join("assets", "gun.png")
        raw_gun = pygame.image.load(gun_path).convert_alpha()
        new_w = int(raw_gun.get_width() * GUN_SCALE)
        new_h = int(raw_gun.get_height() * GUN_SCALE)
        self.gun_image = pygame.transform.scale(raw_gun, (new_w, new_h))
        
        flash_path = os.path.join("assets", "muzzle.png")
        raw_flash = pygame.image.load(flash_path).convert_alpha()
        self.flash_image = pygame.transform.scale(raw_flash, (int(new_w * 0.4), int(new_h * 0.4)))
        
        self.last_shot_time = 0
        self.recoil_offset_x = 0
        self.recoil_offset_y = 0
        self.is_recoiling = False
        self.recoil_start_time = 0
        self.show_flash = False
        self.flash_start_time = 0
        
    def can_shoot(self, current_time):
        return (current_time - self.last_shot_time >= SHOOT_COOLDOWN) and (self.ammo > 0) and not self.is_reloading

    def trigger_shot(self, current_time):
        self.last_shot_time = current_time
        self.ammo -= 1  # Deduct ammo
        
        self.shoot_sound.stop()
        self.shoot_sound.play()
        
        self.show_flash = True
        self.flash_start_time = current_time
        self.is_recoiling = True
        self.recoil_start_time = current_time

    def reload(self, current_time):
        if self.ammo < self.max_ammo and not self.is_reloading:
            self.is_reloading = True
            self.reload_start_time = current_time

    def update(self, current_time):
        # Handle reload timer completion
        if self.is_reloading and (current_time - self.reload_start_time >= self.reload_duration):
            self.ammo = self.max_ammo
            self.is_reloading = False

        if self.show_flash and (current_time - self.flash_start_time > FLASH_DURATION):
            self.show_flash = False
            
        if self.is_recoiling:
            elapsed = current_time - self.recoil_start_time
            if elapsed < SHOOT_COOLDOWN:
                if elapsed < SHOOT_COOLDOWN // 2:
                    progress = elapsed / (SHOOT_COOLDOWN // 2)
                    self.recoil_offset_y = int(progress * 25)
                    self.recoil_offset_x = int(progress * 15)
                else:
                    progress = (elapsed - (SHOOT_COOLDOWN // 2)) / (SHOOT_COOLDOWN // 2)
                    self.recoil_offset_y = int((1 - progress) * 25)
                    self.recoil_offset_x = int((1 - progress) * 15)
            else:
                self.recoil_offset_x = 0
                self.recoil_offset_y = 0
                self.is_recoiling = False
                
    def draw_ui(self, surface):
        base_gun_x = WIDTH - self.gun_image.get_width()
        base_gun_y = HEIGHT - self.gun_image.get_height()
        
        final_gun_x = base_gun_x + self.recoil_offset_x
        final_gun_y = base_gun_y + self.recoil_offset_y
        
        surface.blit(self.gun_image, (final_gun_x, final_gun_y))
        
        if self.show_flash:
            FLASH_OFFSET_X = 250  
            FLASH_OFFSET_Y = 105   
            flash_x = final_gun_x + FLASH_OFFSET_X
            flash_y = final_gun_y + FLASH_OFFSET_Y
            surface.blit(self.flash_image, (flash_x, flash_y))
        
        # HUD Health Bar
        display_health = max(0, self.health)
        pygame.draw.rect(surface, BLACK, (10, 10, 200, 20))
        pygame.draw.rect(surface, GREEN, (10, 10, display_health * 2, 20))
        
        # HUD Ammo Text
        font = pygame.font.SysFont("Arial", 25, bold=True)
        if self.is_reloading:
            ammo_text = font.render("RELOADING...", True, RED)
        else:
            color = RED if self.ammo <= 5 else WHITE
            ammo_text = font.render(f"AMMO: {self.ammo}/{self.max_ammo}", True, color)
        surface.blit(ammo_text, (10, 40))