import pygame, random, math
from collections import deque
from config import font, screen
from utils import clamp01

class FX:
    def __init__(self):
        self.shake_timer = 0
        self.shake_mag = 0
        self.hitstop_timer = 0
        self.particles = deque(maxlen=300)

        self.cracks = deque(maxlen=60)
        self.texts = deque(maxlen=30)

    def hitstop(self, ms=70):
        self.hitstop_timer = ms

    def shake(self, mag=6, ms=120):
        self.shake_mag, self.shake_timer = mag, ms

    def spawn_particles(self, pos, color=(200, 30, 30), count=12, speed=2.2):
        x, y = pos
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(0.4, speed)
            vx, vy = math.cos(ang) * spd, math.sin(ang) * spd
            life = random.randint(300, 650)
            radius = random.randint(2, 4)
            self.particles.append({
                "x": x, "y": y, "vx": vx, "vy": vy,
                "g": 0.02, "life": life, "t": 0, "r": radius,
                "c": color
            })

    def spawn_dust(self, pos, count=14, speed=3.0):
        self.spawn_particles(pos, color=(185, 170, 130), count=count, speed=speed)

    def spawn_crack(self, pos, branches=5, length_rng=(18, 36), life=1500):
        cx, cy = pos
        segs = []
        for _ in range(branches):
            ang = random.uniform(0, 2 * math.pi)
            L = random.uniform(*length_rng)
            x2 = cx + math.cos(ang) * L
            y2 = cy + math.sin(ang) * L
            segs.append(((cx, cy), (x2, y2)))
        self.cracks.append({"segs": segs, "life": life, "t": 0})

    def add_text(self, text, pos, color=(255, 255, 255), life=800):
        x, y = pos
        self.texts.append({"text": text, "x": x, "y": y, "vy": -0.05, "life": life, "t": 0, "color": color})

    def update(self, dt):
        if self.hitstop_timer > 0:
            self.hitstop_timer -= dt
            if self.hitstop_timer < 0:
                self.hitstop_timer = 0
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer < 0:
                self.shake_timer = 0

        alive = deque(maxlen=300)
        for p in self.particles:
            p["t"] += dt
            if p["t"] < p["life"]:
                p["x"] += p["vx"] * (dt / 16)
                p["y"] += p["vy"] * (dt / 16)
                p["vy"] += p["g"] * (dt / 16)
                alive.append(p)
        self.particles = alive

        cracks_alive = deque(maxlen=60)
        for c in self.cracks:
            c["t"] += dt
            if c["t"] < c["life"]:
                cracks_alive.append(c)
        self.cracks = cracks_alive

        texts_alive = deque(maxlen=30)
        for t in self.texts:
            t["t"] += dt
            if t["t"] < t["life"]:
                t["y"] += t["vy"] * dt
                texts_alive.append(t)
        self.texts = texts_alive

    def offset(self):
        if self.shake_timer <= 0:
            return 0, 0
        mag = self.shake_mag * (self.shake_timer / 120.0)
        return random.uniform(-mag, mag), random.uniform(-mag, mag)

    def draw_particles(self):
        for p in self.particles:
            alpha = 255 * (1 - p["t"] / p["life"])
            alpha = max(0, min(255, int(alpha)))
            col = (*p["c"], alpha)
            pygame.draw.circle(screen, col, (int(p["x"]), int(p["y"])), p["r"])

    def draw_cracks(self, surf):
        for c in self.cracks:
            for (x1, y1), (x2, y2) in c["segs"]:
                pygame.draw.line(surf, (80, 55, 40), (int(x1), int(y1)), (int(x2), int(y2)), 2)

    def draw_floating_texts(self, surf):
        for t in self.texts:
            img = font.render(t["text"], True, t["color"])
            rect = img.get_rect(center=(int(t["x"]), int(t["y"])))
            surf.blit(img, rect)