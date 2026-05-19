import pygame
import random

# 1. Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TARGET_SIZE = 60 # Width and height of the target image
TARGET_LIFETIME = 2000 

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Aim Trainer - Enhanced Graphics")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32, bold=True)

# --- GRAPHICS LOADING SYSTEM ---
def load_graphic(filename, size, fallback_color):
    """Tries to load an image. If it fails, creates a colored box instead."""
    try:
        # Load image and keep transparency (convert_alpha)
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        # Fallback if the user hasn't added the .png file yet
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, fallback_color, (0, 0, size[0], size[1]), border_radius=10)
        return surf

# Load our assets (or use fallbacks)
bg_img = load_graphic("background.png", (WIDTH, HEIGHT), (40, 45, 60))
target_img = load_graphic("target.png", (TARGET_SIZE, TARGET_SIZE), (255, 50, 50))
crosshair_img = load_graphic("crosshair.png", (40, 40), (0, 255, 0))

# Hide the default Windows/Mac mouse cursor
pygame.mouse.set_visible(False)

def reset_game():
    return {
        "health": 3,
        "score": 0,
        "targets": [], # Will now hold Pygame Rects for collision
        "spawn_rate": 1000,
        "last_spawn_time": pygame.time.get_ticks(),
        "game_over": False
    }

game_state = reset_game()
running = True

# 2. Main Game Loop
while running:
    current_time = pygame.time.get_ticks()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Draw Background (Replaces screen.fill)
    screen.blit(bg_img, (0, 0))

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_state["game_over"]:
            # Loop backwards to safely remove items
            for target in reversed(game_state["targets"]):
                # Rect.collidepoint checks if the mouse click is inside the image's borders
                if target['rect'].collidepoint((mouse_x, mouse_y)):
                    game_state["targets"].remove(target)
                    game_state["score"] += 1
                    break

    # --- GAME LOGIC ---
    if not game_state["game_over"]:
        # Spawn new targets
        if current_time - game_state["last_spawn_time"] > game_state["spawn_rate"]:
            x = random.randint(0, WIDTH - TARGET_SIZE)
            y = random.randint(50, HEIGHT - TARGET_SIZE)
            
            # Create a Rect for collision detection and positioning
            target_rect = pygame.Rect(x, y, TARGET_SIZE, TARGET_SIZE)
            
            game_state["targets"].append({
                'rect': target_rect, 
                'spawn_time': current_time
            })
            
            game_state["spawn_rate"] = max(350, game_state["spawn_rate"] - 15)
            game_state["last_spawn_time"] = current_time

        # Expire missed targets
        for target in reversed(game_state["targets"]):
            if current_time - target['spawn_time'] > TARGET_LIFETIME:
                game_state["targets"].remove(target)
                game_state["health"] -= 1
                if game_state["health"] <= 0:
                    game_state["game_over"] = True

    # --- DRAWING ---
    if not game_state["game_over"]:
        # Draw all target images
        for target in game_state["targets"]:
            # screen.blit draws the image at the X/Y coordinates of its rect
            screen.blit(target_img, target['rect'])

    # Draw UI text
    score_text = font.render(f"SCORE: {game_state['score']}", True, (255, 255, 255))
    health_text = font.render(f"HEALTH: {'♥ ' * game_state['health']}", True, (255, 50, 50))
    screen.blit(score_text, (20, 10))
    screen.blit(health_text, (WIDTH - 200, 10))

    # Game Over Screen
    if game_state["game_over"]:
        # Re-show the standard mouse cursor when dead
        pygame.mouse.set_visible(True) 
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Semi-transparent black screen
        screen.blit(overlay, (0, 0))
        
        go_text = font.render("GAME OVER - Press 'R' to Restart", True, (255, 255, 255))
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = reset_game()
            pygame.mouse.set_visible(False)

    # Draw Custom Crosshair (Drawn last so it's always on top)
    if not game_state["game_over"]:
        # Center the crosshair image precisely on the mouse tip
        crosshair_rect = crosshair_img.get_rect(center=(mouse_x, mouse_y))
        screen.blit(crosshair_img, crosshair_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()