import pygame, random, sys

pygame.init()
screen = pygame.display.set_mode((700, 400))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load images
zombie_img = pygame.image.load("zombie_head.png")
zombie_img = pygame.transform.scale(zombie_img, (80, 80))
zombie_hit_img = pygame.image.load("zombie_hit.png")  # hình zombie bị đánh
zombie_hit_img = pygame.transform.scale(zombie_hit_img, (80, 80))

hammer_img = pygame.image.load("hammer.png").convert_alpha()
hammer_img = pygame.transform.scale(hammer_img, (100, 100))

offset_x, offset_y = -40, -40

# pygame.mouse.set_visible(False)

# Zombie hole positions
holes = [(150, 150), (350, 150), (550, 150), (150, 300), (350, 300), (550, 300)]

# Game variables
score, miss = 0, 0
zombie_pos = random.choice(holes)
zombie_timer = pygame.time.get_ticks() + 1500

# Zombie hit animation
zombie_hit = False
zombie_hit_timer = 0
zombie_hit_duration = 150  # ms

# Hammer animation
hammer_angle = 0
hammer_phase = 0   # 0 = idle, 1 = lift, 2 = slam, 3 = return
hammer_timer = 0
hammer_duration = 100  # ms mỗi pha

# Sounds
hit_sound = pygame.mixer.Sound("hit.wav")
hit_sound.set_volume(0.3) 
def draw_text(text, x, y):
    img = font.render(text, True, (255,255,255))
    screen.blit(img, (x, y))

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

while True:
    screen.fill((50, 168, 82))

    # Vẽ hố
    for pos in holes:
        pygame.draw.circle(screen, (90, 60, 20), pos, 50)

    # Cập nhật animation búa
    if hammer_phase > 0:
        elapsed = pygame.time.get_ticks() - hammer_timer
        if elapsed > hammer_duration:
            hammer_phase += 1
            hammer_timer = pygame.time.get_ticks()
            if hammer_phase > 3:
                hammer_phase = 0
                hammer_angle = 0
        else:
            progress = elapsed / hammer_duration
            if hammer_phase == 1:  # nhấc lên
                hammer_angle = -30 * progress
            elif hammer_phase == 2:  # đập xuống
                hammer_angle = -30 + 120 * progress
            elif hammer_phase == 3:  # trả về
                hammer_angle = 30 - 90 * progress

    # Vẽ zombie
    if zombie_hit:
        screen.blit(zombie_hit_img, (zombie_pos[0]-40, zombie_pos[1]-40))
        # check hết thời gian bị đánh
        if pygame.time.get_ticks() - zombie_hit_timer > zombie_hit_duration:
            zombie_hit = False
            zombie_pos = random.choice(holes)
            zombie_timer = pygame.time.get_ticks() + 1500
    else:
        screen.blit(zombie_img, (zombie_pos[0]-40, zombie_pos[1]-40))

    # Timer zombie tự đổi nếu chưa bị đánh
    if not zombie_hit and pygame.time.get_ticks() > zombie_timer:
        zombie_pos = random.choice(holes)
        zombie_timer = pygame.time.get_ticks() + 1500

    # Sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            start_hammer_animation()
            mx, my = pygame.mouse.get_pos()
            zx, zy = zombie_pos
            if not zombie_hit and (mx - zx)**2 + (my - zy)**2 <= 50**2:
                score += 1
                hit_sound.play()
                zombie_hit = True
                zombie_hit_timer = pygame.time.get_ticks()
            else:
                miss += 1

    # Điểm số
    draw_text(f"Hit: {score}", 10, 10)
    draw_text(f"Miss: {miss}", 10, 40)
    if score + miss > 0:
        rate = int(score / (score + miss) * 100)
        draw_text(f"Accuracy: {rate}%", 10, 70)

    # Vẽ hammer cuối cùng
    mouse_x, mouse_y = pygame.mouse.get_pos()
    draw_hammer(mouse_x + offset_x, mouse_y + offset_y, hammer_angle)

    pygame.display.update()
    clock.tick(60)
