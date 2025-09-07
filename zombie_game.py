import pygame, random, sys, os, glob, math, time 
from collections import deque

# =============== INIT ===============
pygame.init()
W, H = 700, 400
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Zombie Whack")

# =============== FONTS ===============
font = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)

# =============== LOAD AUDIO ===============
def safe_load_sound(path, vol=0.5):
    if not os.path.isfile(path):
        return None
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(vol)
        return s
    except Exception:
        return None

if os.path.isfile("loon.mp3"):
    try:
        pygame.mixer.music.load("loon.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.4)
    except Exception:
        pass

SND_HIT  = safe_load_sound("hit.wav", 0.35)
SND_POP  = safe_load_sound("pop.wav", 0.35)
SND_MISS = safe_load_sound("miss.wav", 0.25)

# =============== LOAD IMAGES ===============
def safe_img(path, size=None):
    if not os.path.isfile(path):
        surf = pygame.Surface((80,80), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200,60,60), (40,40), 38)
        return pygame.transform.smoothscale(surf, size) if size else surf
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size) if size else img

zombie_img    = safe_img("zombie_head.png", (80,80))
zombie_hit_img= safe_img("zombie_hit.png", (80,80))
hammer_img    = safe_img("hammer.png", (110,110))

# =============== HOLES ===============
holes = [(150, 150), (350, 150), (550, 150),
         (150, 300), (350, 300), (550, 300)]

# =============== UTILS ===============
def lerp(a, b, t): return a + (b - a) * t
def clamp01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def ease_out_cubic(t): t=clamp01(t); return 1-(1-t)**3
def ease_in_cubic(t):  t=clamp01(t); return t**3

def draw_text(text, fnt, color, x, y, center=False):
    img = fnt.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

# =============== FX (shake, hitstop, particles) ===============
class FX:
    def __init__(self):
        self.shake_timer = 0
        self.shake_mag = 0
        self.hitstop_timer = 0
        self.particles = deque(maxlen=300)

    def hitstop(self, ms=70):
        self.hitstop_timer = ms

    def shake(self, mag=6, ms=120):
        self.shake_mag = mag
        self.shake_timer = ms

    def spawn_particles(self, pos, color=(200,30,30), count=12, speed=2.2):
        x,y = pos
        for _ in range(count):
            ang = random.uniform(0, 2*math.pi)
            spd = random.uniform(0.4, speed)
            vx, vy = math.cos(ang)*spd, math.sin(ang)*spd
            life = random.randint(300,650)
            radius = random.randint(2,4)
            self.particles.append({
                "x": x, "y": y, "vx": vx, "vy": vy,
                "g": 0.02, "life": life, "t": 0, "r": radius,
                "c": color
            })

    def update(self, dt):
        if self.hitstop_timer > 0:
            self.hitstop_timer -= dt
            if self.hitstop_timer < 0: self.hitstop_timer = 0

        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer < 0: self.shake_timer = 0

        alive = deque(maxlen=300)
        for p in self.particles:
            p["t"] += dt
            if p["t"] < p["life"]:
                p["x"] += p["vx"] * (dt/16)
                p["y"] += p["vy"] * (dt/16)
                p["vy"] += p["g"] * (dt/16)
                alive.append(p)
        self.particles = alive

    def offset(self):
        if self.shake_timer <= 0: return 0,0
        mag = self.shake_mag * (self.shake_timer/120.0)
        return random.uniform(-mag, mag), random.uniform(-mag, mag)

    def draw_particles(self):
        for p in self.particles:
            alpha = 255 * (1 - p["t"]/p["life"])
            alpha = max(0, min(255, int(alpha)))
            col = (*p["c"], alpha)
            pygame.draw.circle(screen, col, (int(p["x"]), int(p["y"])), p["r"])

# =============== ZOMBIE ===============
class Zombie:
    RISE_MS = 350      # thời gian zombie trồi từ hố lên mặt đất
    IDLE_MS = 3000     # thời gian zombie đứng yên trên mặt đất 
    SINK_MS = 350      # thời gian zombie tự động chui xuống nếu không bị đập
    HIT_SINK_MS = 230  # thời gian zombie chui xuống khi đã bị đập 
    
    def __init__(self, pos):
        self.base = pos
        self.state = "rising"
        self.t0 = pygame.time.get_ticks()
        self.hit = False
        self.y_offset = 40
        self.scale = 0.8
        self.shadow_scale = 0.4
        self.idle_bob_phase = random.uniform(0, math.tau)

    def try_hit(self, mx, my):
        if self.state in ("rising","idle") and not self.hit:
            zx, zy = self.base[0], self.base[1] + int(self.y_offset)
            if (mx - zx)**2 + (my - zy)**2 <= 50**2:
                self.hit = True
                self.state = "hit_sinking"
                self.t0 = pygame.time.get_ticks()
                return True
        return False

    def update(self, dt):
        now = pygame.time.get_ticks()
        if self.state == "rising":
            t = clamp01((now - self.t0)/self.RISE_MS)
            self.y_offset = 40 * (1 - ease_out_cubic(t))
            self.scale = lerp(0.8, 1.0, ease_out_cubic(t))
            self.shadow_scale = lerp(0.4, 1.0, ease_out_cubic(t))
            if t >= 1: self.state, self.t0 = "idle", now

        elif self.state == "idle":
            self.idle_bob_phase += dt*0.008
            bob = math.sin(self.idle_bob_phase) * 2.5
            self.y_offset = bob
            self.scale = 1.0 + math.sin(self.idle_bob_phase*2)*0.01
            if (now - self.t0) >= self.IDLE_MS:
                self.state, self.t0 = "sinking", now

        elif self.state == "sinking":
            t = clamp01((now - self.t0)/self.SINK_MS)
            self.y_offset = 40 * ease_in_cubic(t)
            self.scale = lerp(1.0, 0.9, t)
            self.shadow_scale = lerp(1.0, 0.5, t)
            if t >= 1: return False

        elif self.state == "hit_sinking":
            t = clamp01((now - self.t0)/self.HIT_SINK_MS)
            self.y_offset = 40 * ease_in_cubic(t)
            self.scale = lerp(1.0, 0.85, t)
            self.shadow_scale = lerp(1.0, 0.4, t)
            if t >= 1: return False

        return True

    def draw(self, surf):
        sx, sy = self.base
        shadow_w = int(60 * self.shadow_scale)
        shadow_h = int(18 * self.shadow_scale)
        shadow = pygame.Surface((shadow_w*2, shadow_h*2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,90), (0,0,shadow_w*2,shadow_h*2))
        surf.blit(shadow, (sx-shadow_w, sy-shadow_h+30))

        img = zombie_hit_img if self.hit else zombie_img
        scaled = pygame.transform.smoothscale(img, (int(80*self.scale), int(80*self.scale)))
        rect = scaled.get_rect(center=(sx, sy + int(self.y_offset)))
        surf.blit(scaled, rect)

# =============== HAMMER ===============
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

# =============== GAME ===============
class Game:
    def __init__(self):
        self.fx = FX()
        self.hammer = Hammer()

        self.hit = 0
        self.miss = 0
        self.combo = 0
        self.combo_time = 0
        self.combo_window = 1200
        self.zombies = []
        self.wave_timer = 0
        self.game_end_time = 0
        self.state = "playing"  

        self.btn_rect = pygame.Rect(250, 280, 200, 50)
        self.reset()

    def reset(self):
        now = pygame.time.get_ticks()
        self.hit = self.miss = self.combo = 0
        self.combo_time = now
        self.zombies.clear()
        self.wave_timer = now + 1200
        self.game_end_time = now + 60000
        self.state = "playing"
        try:
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.4)
        except Exception:
            pass

    def spawn_wave(self):
        self.zombies.clear()
        n = random.choices([1,2,3], weights=[0.55,0.33,0.12], k=1)[0]
        for pos in random.sample(holes, k=n):
            self.zombies.append(Zombie(pos))
        if SND_POP: SND_POP.play()

    def try_hit(self, mx, my):
        for z in reversed(self.zombies):
            if z.try_hit(mx, my):
                self.hit += 1
                self.combo += 1
                self.combo_time = pygame.time.get_ticks()
                if SND_HIT: SND_HIT.play()
                self.fx.hitstop(65)
                self.fx.shake(6, 110)
                self.fx.spawn_particles(z.base, (210,40,40), count=14, speed=2.5)
                return True
        self.miss += 1
        self.combo = 0
        if SND_MISS: SND_MISS.play()
        self.fx.shake(3, 60)
        return False

    def on_click(self, mx, my):
        if self.state == "playing":
            self.hammer.start()
            _ = self.try_hit(mx, my)
        elif self.state == "game_over":
            if self.btn_rect.collidepoint((mx,my)):
                self.reset()

    def update(self, dt):
        self.fx.update(dt)

        if self.state == "game_over":
            return

        if self.fx.hitstop_timer > 0:
            return

        now = pygame.time.get_ticks()
        if now >= self.game_end_time:
            self.state = "game_over"
            return

        if now > self.wave_timer and not self.zombies:
            self.spawn_wave()
            self.wave_timer = now + 1500

        alive = []
        for z in self.zombies:
            if z.update(dt):
                alive.append(z)
        self.zombies = alive

        self.hammer.update()

    def draw_world(self):
        screen.fill((46, 168, 82))

        for i in range(6):
            y = 90 + i*50
            pygame.draw.rect(screen, (40, 150, 75) if i%2==0 else (44,160,80), (0,y,W,40), 0, border_radius=8)

        for pos in holes:
            pygame.draw.circle(screen, (90, 60, 20), pos, 50)

        for z in self.zombies:
            z.draw(screen)

        self.fx.draw_particles()

        now = pygame.time.get_ticks()
        time_left = max(0, (self.game_end_time - now)//1000)
        draw_text(f"Time: {time_left}", font, (255,255,255), W-160, 10)
        draw_text(f"Hit: {self.hit}", font, (255,255,255), 10, 10)
        draw_text(f"Miss: {self.miss}", font, (255,255,255), 10, 40)
        total = self.hit + self.miss
        acc = int(self.hit/total*100) if total>0 else 0
        draw_text(f"Acc: {acc}%", font, (255,255,255), 10, 70)

        if self.combo >= 2:
            draw_text(f"COMBO x{self.combo}", font_medium, (255,255,255), W//2, 20, center=True)


    def draw_game_over(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0,0,0,150))
        screen.blit(s, (0,0))

        popup_rect = pygame.Rect(150, 50, 400, 300)
        pygame.draw.rect(screen, (45,52,71), popup_rect, border_radius=15)
        cx = popup_rect.centerx

        draw_text("Time's Up!", font_large, (255,223,0), cx, 100, center=True)
        draw_text(f"Hits: {self.hit}", font_medium, (255,255,255), cx, 165, center=True)
        draw_text(f"Misses: {self.miss}", font_medium, (255,255,255), cx, 205, center=True)
        total = self.hit + self.miss
        acc = int(self.hit/total*100) if total>0 else 0
        draw_text(f"Accuracy: {acc}%", font_medium, (255,255,255), cx, 245, center=True)

        self.btn_rect.centerx = cx
        self.btn_rect.y = 290
        pygame.draw.rect(screen, (0,177,64), self.btn_rect, border_radius=10)
        draw_text("Tap to try again", font, (255,255,255), self.btn_rect.centerx, self.btn_rect.centery, center=True)

    def draw(self, mx, my):
        ox, oy = self.fx.offset()
        self.draw_world()

        if self.state == "game_over":
            self.draw_game_over()

        self.hammer.draw(mx, my)

        if ox or oy:
            frame = screen.copy()
            screen.fill((46,168,82))
            screen.blit(frame, (int(ox), int(oy)))

# =============== MAIN LOOP ===============
def main():
    game = Game()
    offset_x, offset_y = -30, -30

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
