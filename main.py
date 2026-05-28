import pygame
import random
import os
import json
from settings import *
from player import Player
from enemy import Zombie

def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Z Shooter")
    clock = pygame.time.Clock()
    
    game_state = "MENU"
    player_name = ""
    error_msg = ""
    
    font = pygame.font.SysFont("Arial", 40, bold=True)
    sub_font = pygame.font.SysFont("Arial", 25)
    
    crosshair_path = os.path.join("assets", "crosshair.png")
    
    try:
        crosshair_img = pygame.image.load(crosshair_path).convert_alpha()
        crosshair_img = pygame.transform.scale(crosshair_img, (40, 40))
    except:
        crosshair_img = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(crosshair_img, RED, (10, 10), 10, 2)

    reload_sound_path = os.path.join("assets", "reload.wav")
    
    try:
        reload_sound = pygame.mixer.Sound(reload_sound_path)
    except:
        reload_sound = None

    def load_leaderboard():
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            except:
                return {}
        return {}

    def save_score(name, final_score):
        lb = load_leaderboard()
        lb[name] = max(lb.get(name, 0), final_score)

        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(lb, f)

    bg_path = os.path.join("assets", "background.png")
    background = pygame.image.load(bg_path).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    
    player = Player()
    zombies = []
    
    wave = 1
    score = 0
    zombies_killed_in_wave = 0
    zombies_to_spawn = 0
    last_spawn_time = 0
    transition_start_time = 0
    
    def reset_game():
        nonlocal player, zombies, wave, score, zombies_killed_in_wave, transition_start_time, game_state

        player = Player()
        zombies = []

        wave = 1
        score = 0
        zombies_killed_in_wave = 0

        transition_start_time = pygame.time.get_ticks()
        game_state = "WAVE_TRANSITION"

    game_over = False
    won_game = False
    score_saved = False
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        screen.fill(BLACK)

        if game_state == "PLAYING" and not game_over and not won_game:
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

        if game_state == "MENU":
            title_text = font.render("Z SHOOTER", True, RED)
            screen.blit(title_text, title_text.get_rect(center=(WIDTH//2, 70)))
            
            play_text = font.render("PLAY", True, WHITE)
            play_rect = play_text.get_rect(center=(WIDTH//2, 150))

            is_hovering = play_rect.collidepoint(mouse_pos)

            screen.blit(play_text, play_rect)
            
            if is_hovering:
                pygame.draw.line(
                    screen,
                    WHITE,
                    (play_rect.left, play_rect.bottom),
                    (play_rect.right, play_rect.bottom),
                    3
                )
                
            lb_header = sub_font.render("--- TOP ZOMBIE KILLERS ---", True, RED)

            screen.blit(
                lb_header,
                lb_header.get_rect(center=(WIDTH//2, 230))
            )
            
            lb_data = load_leaderboard()

            sorted_lb = sorted(
                lb_data.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            y_offset = 270

            for rank, (name, s) in enumerate(sorted_lb):
                lb_text = sub_font.render(
                    f"{rank + 1}. {name} - {s} Kills",
                    True,
                    WHITE
                )

                screen.blit(
                    lb_text,
                    lb_text.get_rect(center=(WIDTH//2, y_offset))
                )

                y_offset += 35
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                    game_state = "INPUT"

        elif game_state == "INPUT":
            prompt = font.render(
                "Enter Name: " + player_name,
                True,
                WHITE
            )

            screen.blit(prompt, (150, HEIGHT//2 - 50))

            screen.blit(
                sub_font.render(error_msg, True, RED),
                (150, HEIGHT//2)
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and player_name:
                        if player_name not in load_leaderboard():
                            score_saved = False
                            game_over = False
                            won_game = False

                            reset_game()
                        else:
                            error_msg = "Name already taken!"

                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]

                    else:
                        player_name += event.unicode

        elif game_state == "WAVE_TRANSITION":
            screen.blit(background, (0, 0))

            wave_text = font.render(
                f"WAVE {wave}",
                True,
                RED
            )

            screen.blit(
                wave_text,
                wave_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            )

            player.draw_ui(screen)

            if current_time - transition_start_time > 2000:
                zombies_to_spawn = wave * 5
                zombies_killed_in_wave = 0
                last_spawn_time = current_time

                game_state = "PLAYING"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        elif game_state == "PLAYING":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not won_game:
                    if event.button == 1:
                        if player.ammo <= 0:
                            if not player.is_reloading:
                                player.reload(current_time)

                                if reload_sound:
                                    reload_sound.play()

                        elif player.can_shoot(current_time):
                            player.trigger_shot(current_time)

                            for z in reversed(zombies):
                                if z.check_shot(mouse_pos, player.gun_damage):
                                    z.last_hit_time = current_time
                                    break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not game_over and not won_game:
                        game_state = "PAUSED"

                    elif event.key == pygame.K_r and not game_over and not won_game:
                        if player.ammo < 30 and not player.is_reloading:
                            player.reload(current_time)

                            if reload_sound:
                                reload_sound.play()

                    elif (game_over or won_game) and event.key == pygame.K_r:
                        game_state = "MENU"
                        player_name = ""

            if not game_over and not won_game:
                player.update(current_time)

                current_cooldown = max(
                    400,
                    SPAWN_COOLDOWN - (wave * 150)
                )
                
                if zombies_to_spawn > 0 and (
                    current_time - last_spawn_time > current_cooldown
                ):
                    zombies.append(
                        Zombie(
                            random.randint(100, WIDTH - 100),
                            ZOMBIE_SPAWN_Y
                        )
                    )

                    zombies_to_spawn -= 1
                    last_spawn_time = current_time

                for z in zombies:
                    z.update(player)
                
                old_count = len(zombies)

                zombies = [z for z in zombies if z.health > 0]

                killed_now = old_count - len(zombies)
                
                score += killed_now
                zombies_killed_in_wave += killed_now
                
                target_kills = wave * 5

                if (
                    len(zombies) == 0 and
                    zombies_to_spawn == 0 and
                    zombies_killed_in_wave < target_kills
                ):
                    zombies_to_spawn = (
                        target_kills - zombies_killed_in_wave
                    )
                    
                if zombies_killed_in_wave >= target_kills:
                    if wave == 10:
                        won_game = True
                    else:
                        wave += 1

                        zombies.clear()

                        transition_start_time = current_time
                        game_state = "WAVE_TRANSITION"

                if player.health <= 0:
                    game_over = True

            if (game_over or won_game) and not score_saved:
                save_score(player_name, score)
                score_saved = True

            screen.blit(background, (0, 0))

            zombies.sort(key=lambda z: z.scale)

            for z in zombies:
                z.draw(screen)

            player.draw_ui(screen)
            
            hud_text = sub_font.render(
                f"Wave: {wave}/10  |  Kills: {score}",
                True,
                WHITE
            )

            screen.blit(hud_text, (WIDTH - 250, 10))
            
            if not game_over and not won_game:
                crosshair_rect = crosshair_img.get_rect(center=mouse_pos)
                screen.blit(crosshair_img, crosshair_rect)
            
            if game_over or won_game:
                overlay = pygame.Surface(
                    (WIDTH, HEIGHT),
                    pygame.SRCALPHA
                )

                overlay.fill((0, 0, 0, 180))

                screen.blit(overlay, (0, 0))
                
                end_msg = (
                    "YOU SURVIVED!"
                    if won_game
                    else "GAME OVER"
                )

                color = GREEN if won_game else RED
                
                end_text = font.render(end_msg, True, color)

                screen.blit(
                    end_text,
                    end_text.get_rect(
                        center=(WIDTH//2, HEIGHT//2 - 30)
                    )
                )
                
                restart_text = sub_font.render(
                    "Press 'R' to return to Menu",
                    True,
                    WHITE
                )

                screen.blit(
                    restart_text,
                    restart_text.get_rect(
                        center=(WIDTH//2, HEIGHT//2 + 20)
                    )
                )

        elif game_state == "PAUSED":
            resume_text = font.render("RESUME", True, WHITE)

            exit_text = font.render(
                "EXIT TO MENU",
                True,
                WHITE
            )

            resume_rect = resume_text.get_rect(
                center=(WIDTH//2, HEIGHT//2 - 20)
            )

            exit_rect = exit_text.get_rect(
                center=(WIDTH//2, HEIGHT//2 + 40)
            )

            resume_hover = resume_rect.collidepoint(mouse_pos)
            exit_hover = exit_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_ESCAPE
                ):
                    game_state = "PLAYING"

                if (
                    event.type == pygame.MOUSEBUTTONDOWN and
                    event.button == 1
                ):
                    if resume_hover:
                        game_state = "PLAYING"

                    if exit_hover:
                        game_state = "MENU"
                        player_name = ""
            
            screen.blit(background, (0, 0))

            for z in zombies:
                z.draw(screen)

            player.draw_ui(screen)
            
            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 180))

            screen.blit(overlay, (0, 0))
            
            paused_text = font.render("PAUSED", True, RED)

            screen.blit(
                paused_text,
                paused_text.get_rect(
                    center=(WIDTH//2, HEIGHT//2 - 100)
                )
            )
            
            screen.blit(resume_text, resume_rect)
            screen.blit(exit_text, exit_rect)
            
            if resume_hover:
                pygame.draw.line(
                    screen,
                    WHITE,
                    (resume_rect.left, resume_rect.bottom),
                    (resume_rect.right, resume_rect.bottom),
                    3
                )

            if exit_hover:
                pygame.draw.line(
                    screen,
                    WHITE,
                    (exit_rect.left, exit_rect.bottom),
                    (exit_rect.right, exit_rect.bottom),
                    3
                )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()