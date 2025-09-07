import pygame, random
import config as cfg

def load_assets():
    """Load hình ảnh, âm thanh"""
    zombie_img = pygame.image.load(cfg.ZOMBIE_IMG)
    zombie_img = pygame.transform.scale(zombie_img, cfg.ZOMBIE_SIZE)

    zombie_hit_img = pygame.image.load(cfg.ZOMBIE_HIT_IMG)
    zombie_hit_img = pygame.transform.scale(zombie_hit_img, cfg.ZOMBIE_SIZE)

    hammer_img = pygame.image.load(cfg.HAMMER_IMG).convert_alpha()
    hammer_img = pygame.transform.scale(hammer_img, cfg.HAMMER_SIZE)

    hit_sound = pygame.mixer.Sound(cfg.HIT_SOUND_FILE)
    hit_sound.set_volume(0.3)

    return zombie_img, zombie_hit_img, hammer_img, hit_sound

def reset_game():
    current_time = pygame.time.get_ticks()
    return {
        'hit': 0,
        'miss': 0,
        'zombies': [],
        'wave_timer': current_time + cfg.WAVE_INTERVAL,
        'game_end_time': current_time + cfg.GAME_DURATION,
        'game_state': 'playing'
    }

def draw_text(text, font, color, surface, x, y, center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)    
    else:
        text_rect.topleft = (x, y) 
    surface.blit(text_obj, text_rect)


def draw_hammer(screen, hammer_img, mouse_x, mouse_y, angle):
    rotated = pygame.transform.rotate(hammer_img, angle)
    rect = rotated.get_rect()
    rect.midtop = (mouse_x, mouse_y)
    screen.blit(rotated, rect)

def spawn_new_wave(game_vars):
    game_vars['zombies'].clear()
    num_zombies = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1], k=1)[0]
    positions = random.sample(cfg.HOLES, k=num_zombies)
    for pos in positions:
        game_vars['zombies'].append({'pos': pos, 'hit': False, 'hit_timer': 0})
