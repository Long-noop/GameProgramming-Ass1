import pygame

pygame.init()

W, H = 700, 400
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Zombie Whack")

# Fonts
font = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)

# Holes
holes = [(150, 150), (350, 150), (550, 150),
         (150, 300), (350, 300), (550, 300)]
