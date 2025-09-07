import pygame, sys
import config as cfg
import utils

pygame.init()
screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load and play background music
pygame.mixer.music.load(cfg.MUSIC_FILE)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Load assets
zombie_img, zombie_hit_img, hammer_img, hit_sound = utils.load_assets()

# --- Game State ---
game_vars = utils.reset_game()

# Hammer animation
hammer_angle, hammer_phase, hammer_timer = 0, 0, 0

button_rect = pygame.Rect(250, 280, 200, 50)

def start_hammer_animation():
    global hammer_phase, hammer_timer
    if hammer_phase == 0:
        hammer_phase = 1
        hammer_timer = pygame.time.get_ticks()

while True:
    mx, my = pygame.mouse.get_pos()

    # --- Event ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_vars['game_state'] == 'playing':
                start_hammer_animation()
                hit_registered = False
                for zombie in game_vars['zombies']:
                    if not zombie['hit']:
                        zx, zy = zombie['pos']
                        if (mx - zx)**2 + (my - zy)**2 <= 50**2:
                            game_vars['hit'] += 1
                            hit_sound.play()
                            zombie['hit'] = True
                            zombie['hit_timer'] = pygame.time.get_ticks()
                            hit_registered = True
                            break
                if not hit_registered:
                    game_vars['miss'] += 1

            elif game_vars['game_state'] == 'game_over':
                if button_rect.collidepoint(mx, my):
                    game_vars = utils.reset_game()

    # --- Update & Draw ---
    screen.fill((50, 168, 82))
    current_time = pygame.time.get_ticks()

    if game_vars['game_state'] == 'playing':
        if current_time >= game_vars['game_end_time']:
            game_vars['game_state'] = 'game_over'

        for pos in cfg.HOLES:
            pygame.draw.circle(screen, (90, 60, 20), pos, 50)

        # Hammer animation
        if hammer_phase > 0:
            elapsed = pygame.time.get_ticks() - hammer_timer
            if elapsed > cfg.HAMMER_DURATION:
                hammer_phase += 1; hammer_timer = pygame.time.get_ticks()
                if hammer_phase > 3: hammer_phase = 0; hammer_angle = 0
            else:
                progress = elapsed / cfg.HAMMER_DURATION
                if hammer_phase == 1: hammer_angle = -30 * progress
                elif hammer_phase == 2: hammer_angle = -30 + 120 * progress
                elif hammer_phase == 3: hammer_angle = 30 - 90 * progress

        # Spawn zombies
        if current_time > game_vars['wave_timer']:
            utils.spawn_new_wave(game_vars)
            game_vars['wave_timer'] = current_time + cfg.WAVE_INTERVAL

        for zombie in game_vars['zombies'][:]:
            img_to_draw = zombie_hit_img if zombie['hit'] else zombie_img
            screen.blit(img_to_draw, (zombie['pos'][0] - 40, zombie['pos'][1] - 40))
            if zombie['hit'] and current_time - zombie['hit_timer'] > cfg.ZOMBIE_HIT_DURATION:
                game_vars['zombies'].remove(zombie)

        if not game_vars['zombies']:
            utils.spawn_new_wave(game_vars)
            game_vars['wave_timer'] = current_time + cfg.WAVE_INTERVAL

        # HUD
        time_left = max((game_vars['game_end_time'] - current_time) // 1000, 0)
        utils.draw_text(f"Time Left: {time_left}", cfg.FONT_SMALL, (255,255,255), screen, 520, 10)
        utils.draw_text(f"Hit: {game_vars['hit']}", cfg.FONT_SMALL, (255,255,255), screen, 10, 10)
        utils.draw_text(f"Miss: {game_vars['miss']}", cfg.FONT_SMALL, (255,255,255), screen, 10, 40)
        total = game_vars['hit'] + game_vars['miss']
        rate = int(game_vars['hit'] / total * 100) if total > 0 else 0
        utils.draw_text(f"Accuracy: {rate}%", cfg.FONT_SMALL, (255,255,255), screen, 10, 70)

    elif game_vars['game_state'] == 'game_over':
        s = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0, 0))

        popup_rect = pygame.Rect(150, 50, 400, 300)
        pygame.draw.rect(screen, (45, 52, 71), popup_rect, border_radius=15)

        popup_center_x = popup_rect.centerx
        utils.draw_text("Time's Up!", cfg.FONT_LARGE, (255,223,0), screen, popup_center_x, 100, center=True)
        utils.draw_text(f"Hits: {game_vars['hit']}", cfg.FONT_MEDIUM, (255,255,255), screen, popup_center_x, 165, center=True)
        utils.draw_text(f"Misses: {game_vars['miss']}", cfg.FONT_MEDIUM, (255,255,255), screen, popup_center_x, 205, center=True)
        total = game_vars['hit'] + game_vars['miss']
        rate = int(game_vars['hit'] / total * 100) if total > 0 else 0
        utils.draw_text(f"Accuracy: {rate}%", cfg.FONT_MEDIUM, (255,255,255), screen, popup_center_x, 245, center=True)

        button_rect.centerx = popup_center_x
        button_rect.y = 290
        pygame.draw.rect(screen, (0,177,64), button_rect, border_radius=10)
        utils.draw_text("Tap to try again", cfg.FONT_SMALL, (255,255,255), screen, button_rect.centerx, button_rect.centery, center=True)

    utils.draw_hammer(screen, hammer_img, mx + cfg.OFFSET_X, my + cfg.OFFSET_Y, hammer_angle)
    pygame.display.update()
    clock.tick(cfg.FPS)
