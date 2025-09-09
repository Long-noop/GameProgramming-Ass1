import pygame
from config import screen
from utils import safe_img

hammer_img = safe_img("../assets/hammer.png", (110,110))

class Hammer:
    def __init__(self):
        self.angle = 0
        self.phase = 0
        self.t0 = 0
        self.D = 90

    def start(self):
        if self.phase == 0:
            self.phase = 1
            self.t0 = pygame.time.get_ticks()

    def update(self):
        if self.phase == 0: return
        t = pygame.time.get_ticks() - self.t0
        if t > self.D:
            self.phase += 1
            self.t0 = pygame.time.get_ticks()
            if self.phase > 3:
                self.phase = 0
                self.angle = 0
            return
        p = t / self.D
        if self.phase == 1: self.angle = -25 * p
        elif self.phase == 2: self.angle = -25 + 140 * p
        elif self.phase == 3: self.angle = 115 - 115 * p

    def draw(self, mx, my):
        rot = pygame.transform.rotate(hammer_img, self.angle)
        rect = rot.get_rect()
        rect.midtop = (mx-20, my-20)
        screen.blit(rot, rect)