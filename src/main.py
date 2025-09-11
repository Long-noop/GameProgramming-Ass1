import pygame, sys
from config import clock
from game import Game
from utils import intro_screen

def main():
    intro_screen()
    
    game = Game()
    offset_x, offset_y = -30, -30

    try:
        pygame.mixer.music.load("../assets/loon.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Không load được nhạc:", e)
    
    while True:
        dt = clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                game.on_click(mx, my)
        game.update(dt)
        game.draw(mx + offset_x, my + offset_y)
        pygame.display.flip()

if __name__ == "__main__":
    main()
