import pygame

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Test Pygame")

running = True
while running:
    screen.fill((100, 200, 255))  # light blue
    pygame.draw.circle(screen, (255, 0, 0), (200, 150), 40)  # red circle

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()

