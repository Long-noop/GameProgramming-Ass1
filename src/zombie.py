import pygame, random, math
from utils import clamp01, lerp, ease_out_cubic, ease_in_cubic
from config import screen
from utils import safe_img

zombie_img     = safe_img("../assets/zombie_head.png", (80,80))
zombie_hit_img = safe_img("../assets/zombie_hit.png", (80,80))
zombie_black_img = safe_img("../assets/zombie_black.png", (80,80))
zombie_gold_img  = safe_img("../assets/zombie_gold.png", (80,80))

class Zombie:
    RISE_MS = 350
    IDLE_MS = 3000
    SINK_MS = 350
    HIT_SINK_MS = 230

    def __init__(self, pos, ztype="normal"):
        self.base = pos
        self.state = "rising"
        self.t0 = pygame.time.get_ticks()
        self.hit = False
        self.y_offset = 40
        self.scale = 0.8
        self.shadow_scale = 0.4
        self.idle_bob_phase = random.uniform(0, getattr(math, "tau", 2*math.pi))
        self.ztype = ztype

    def try_hit(self, mx, my):
        if self.state in ("rising", "idle") and not self.hit:
            zx, zy = self.base[0], self.base[1] + int(self.y_offset)
            if (mx - zx) ** 2 + (my - zy) ** 2 <= 50 ** 2:
                self.hit = True
                self.state = "hit_sinking"
                self.t0 = pygame.time.get_ticks()
                return True
        return False

    def update(self, dt):
        now = pygame.time.get_ticks()
        if self.state == "rising":
            t = clamp01((now - self.t0) / self.RISE_MS)
            self.y_offset = 40 * (1 - ease_out_cubic(t))
            self.scale = lerp(0.8, 1.0, ease_out_cubic(t))
            self.shadow_scale = lerp(0.4, 1.0, ease_out_cubic(t))
            if t >= 1:
                self.state, self.t0 = "idle", now

        elif self.state == "idle":
            self.idle_bob_phase += dt * 0.008
            bob = math.sin(self.idle_bob_phase) * 2.5
            self.y_offset = bob
            self.scale = 1.0 + math.sin(self.idle_bob_phase * 2) * 0.01
            if (now - self.t0) >= self.IDLE_MS:
                self.state, self.t0 = "sinking", now

        elif self.state == "sinking":
            t = clamp01((now - self.t0) / self.SINK_MS)
            self.y_offset = 40 * ease_in_cubic(t)
            self.scale = lerp(1.0, 0.9, t)
            self.shadow_scale = lerp(1.0, 0.5, t)
            if t >= 1:
                return False

        elif self.state == "hit_sinking":
            t = clamp01((now - self.t0) / self.HIT_SINK_MS)
            self.y_offset = 40 * ease_in_cubic(t)
            self.scale = lerp(1.0, 0.85, t)
            self.shadow_scale = lerp(1.0, 0.4, t)
            if t >= 1:
                return False

        return True

    def draw(self, surf):
        sx, sy = self.base
        shadow_w = int(60 * self.shadow_scale)
        shadow_h = int(18 * self.shadow_scale)
        shadow = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, shadow_w * 2, shadow_h * 2))
        surf.blit(shadow, (sx - shadow_w, sy - shadow_h + 30))

        if self.ztype == "normal":
            img = zombie_hit_img if self.hit else zombie_img
        elif self.ztype == "black":
            img = zombie_black_img
        elif self.ztype == "gold":
            img = zombie_gold_img
            
        scaled = pygame.transform.smoothscale(img, (int(80 * self.scale), int(80 * self.scale)))
        rect = scaled.get_rect(center=(sx, sy + int(self.y_offset)))
        surf.blit(scaled, rect)