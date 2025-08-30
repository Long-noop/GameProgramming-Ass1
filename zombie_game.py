import pygame, random, sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load zombie image
zombie_img = pygame.image.load("zombie_head.png")
zombie_img = pygame.transform.scale(zombie_img, (80, 80))

# Zombie hole positions
holes = [(150, 150), (350, 150), (550, 150), (150, 300), (350, 300), (550, 300)]

# Game variables
score = 0
miss = 0
zombie_pos = random.choice(holes)
zombie_timer = pygame.time.get_ticks() + 1500  # disappear after 1.5s

# Sounds
hit_sound = pygame.mixer.Sound("hit.wav")
# pygame.mixer.music.load("bg_music.mp3")
# pygame.mixer.music.play(-1)

def draw_text(text, x, y):
    img = font.render(text, True, (255,255,255))
    screen.blit(img, (x, y))

while True:
    screen.fill((50, 168, 82))  # Background green

    # Draw holes
    for pos in holes:
        pygame.draw.circle(screen, (90, 60, 20), pos, 50)

    # Draw zombie
    screen.blit(zombie_img, (zombie_pos[0]-40, zombie_pos[1]-40))

    # Check zombie timer
    if pygame.time.get_ticks() > zombie_timer:
        zombie_pos = random.choice(holes)
        zombie_timer = pygame.time.get_ticks() + 1500

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            zx, zy = zombie_pos
            if (mx - zx)**2 + (my - zy)**2 <= 50**2:
                score += 1
                hit_sound.play()
                zombie_pos = random.choice(holes)
                zombie_timer = pygame.time.get_ticks() + 1500
            else:
                miss += 1

    # Draw score
    draw_text(f"Hit: {score}", 10, 10)
    draw_text(f"Miss: {miss}", 10, 40)
    if score + miss > 0:
        rate = int(score / (score + miss) * 100)
        draw_text(f"Accuracy: {rate}%", 10, 70)

    pygame.display.update()
    clock.tick(60)



















