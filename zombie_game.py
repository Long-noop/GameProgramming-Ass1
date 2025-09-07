import pygame, random, sys

pygame.init()
screen = pygame.display.set_mode((700, 400))
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)

# Load and play background music
pygame.mixer.music.load("loon.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Load images
zombie_img = pygame.image.load("zombie_head.png")
zombie_img = pygame.transform.scale(zombie_img, (80, 80))
zombie_hit_img = pygame.image.load("zombie_hit.png")
zombie_hit_img = pygame.transform.scale(zombie_hit_img, (80, 80))

hammer_img = pygame.image.load("hammer.png").convert_alpha()
hammer_img = pygame.transform.scale(hammer_img, (100, 100))

offset_x, offset_y = -40, -40

# Zombie hole positions
holes = [(150, 150), (350, 150), (550, 150), (150, 300), (350, 300), (550, 300)]

# --- Game State and Variables ---
game_vars = {
    'hit': 0,
    'miss': 0,
    'zombies': [],
    'wave_timer': 0,
    'game_end_time': 0, 
    'game_state': 'playing'
}

zombie_hit_duration = 150 # ms

# Hammer animation
hammer_angle = 0
hammer_phase = 0
hammer_timer = 0
hammer_duration = 100

# Sounds
hit_sound = pygame.mixer.Sound("hit.wav")
hit_sound.set_volume(0.3)

def reset_game():
    global game_vars
    current_time = pygame.time.get_ticks()
    game_vars = {
        'hit': 0,
        'miss': 0,
        'zombies': [],
        'wave_timer': current_time + 1500,
        'game_end_time': current_time + 60000, # 60 seconds from now
        'game_state': 'playing'
    }
    pygame.mixer.music.play(-1)

def draw_text(text, font, color, surface, x, y, center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

def draw_hammer(mouse_x, mouse_y, angle):
    rotated = pygame.transform.rotate(hammer_img, angle)
    rect = rotated.get_rect()
    rect.midtop = (mouse_x, mouse_y)
    screen.blit(rotated, rect)

def start_hammer_animation():
    global hammer_phase, hammer_timer
    if hammer_phase == 0:
        hammer_phase = 1
        hammer_timer = pygame.time.get_ticks()

# Spawn logic
def spawn_new_wave():
    game_vars['zombies'].clear()
    num_zombies = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1], k=1)[0]
    positions = random.sample(holes, k=num_zombies)
    
    for pos in positions:
        game_vars['zombies'].append({'pos': pos, 'hit': False, 'hit_timer': 0})

reset_game()
button_rect = pygame.Rect(250, 280, 200, 50)

while True:
    mx, my = pygame.mouse.get_pos()
    
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
                    reset_game()

    screen.fill((50, 168, 82))

    if game_vars['game_state'] == 'playing':
        # Check the timer to end the game
        current_time = pygame.time.get_ticks()
        if current_time >= game_vars['game_end_time']:
            game_vars['game_state'] = 'game_over'

        for pos in holes:
            pygame.draw.circle(screen, (90, 60, 20), pos, 50)

        if hammer_phase > 0:
            elapsed = pygame.time.get_ticks() - hammer_timer
            if elapsed > hammer_duration:
                hammer_phase += 1; hammer_timer = pygame.time.get_ticks()
                if hammer_phase > 3: hammer_phase = 0; hammer_angle = 0
            else:
                progress = elapsed / hammer_duration
                if hammer_phase == 1: hammer_angle = -30 * progress
                elif hammer_phase == 2: hammer_angle = -30 + 120 * progress
                elif hammer_phase == 3: hammer_angle = 30 - 90 * progress

        if current_time > game_vars['wave_timer']:
            spawn_new_wave()
            game_vars['wave_timer'] = current_time + 1500

        for zombie in game_vars['zombies'][:]:
            img_to_draw = zombie_hit_img if zombie['hit'] else zombie_img
            screen.blit(img_to_draw, (zombie['pos'][0] - 40, zombie['pos'][1] - 40))
            if zombie['hit'] and pygame.time.get_ticks() - zombie['hit_timer'] > zombie_hit_duration:
                game_vars['zombies'].remove(zombie)

        # Display the timer
        time_left = (game_vars['game_end_time'] - current_time) // 1000
        if time_left < 0: time_left = 0
        draw_text(f"Time Left: {time_left}", font, (255, 255, 255), screen, 520, 10)

        # Score display
        draw_text(f"Hit: {game_vars['hit']}", font, (255, 255, 255), screen, 10, 10)
        draw_text(f"Miss: {game_vars['miss']}", font, (255, 255, 255), screen, 10, 40)
        total = game_vars['hit'] + game_vars['miss']
        rate = int(game_vars['hit'] / total * 100) if total > 0 else 0
        draw_text(f"Accuracy: {rate}%", font, (255, 255, 255), screen, 10, 70)
    
    elif game_vars['game_state'] == 'game_over':
        s = pygame.Surface((700, 400), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0, 0))

        popup_rect = pygame.Rect(150, 50, 400, 300)
        pygame.draw.rect(screen, (45, 52, 71), popup_rect, border_radius=15)
        
        popup_center_x = popup_rect.centerx

        # Display final result
        draw_text("Time's Up!", font_large, (255, 223, 0), screen, popup_center_x, 100, center=True)
        draw_text(f"Hits: {game_vars['hit']}", font_medium, (255, 255, 255), screen, popup_center_x, 165, center=True)
        draw_text(f"Misses: {game_vars['miss']}", font_medium, (255, 255, 255), screen, popup_center_x, 205, center=True)
        total = game_vars['hit'] + game_vars['miss']
        rate = int(game_vars['hit'] / total * 100) if total > 0 else 0
        draw_text(f"Accuracy: {rate}%", font_medium, (255, 255, 255), screen, popup_center_x, 245, center=True)

        button_rect.centerx = popup_center_x
        button_rect.y = 290
        pygame.draw.rect(screen, (0, 177, 64), button_rect, border_radius=10)
        draw_text("Tap to try again", font, (255, 255, 255), screen, button_rect.centerx, button_rect.centery, center=True)

    draw_hammer(mx + offset_x, my + offset_y, hammer_angle)

    pygame.display.update()
    clock.tick(60)
