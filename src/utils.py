import os, json, pygame, math
from config import screen

RECORD_PATH = "best_record.json"

def load_best():
    if os.path.isfile(RECORD_PATH):
        try:
            with open(RECORD_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_best(data):
    try:
        with open(RECORD_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def is_better(new, old):
    if old is None:
        return True
    if new.get("acc", 0) >= old.get("acc", 0) and new.get("hit", 0) > old.get("hit", 0):
        return True
    return False

def safe_load_sound(path, vol=0.5):
    if not os.path.isfile(path):
        return None
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(vol)
        return s
    except Exception:
        return None

def safe_img(path, size=None):
    if not os.path.isfile(path):
        surf = pygame.Surface((80,80), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200,60,60), (40,40), 38)
        return pygame.transform.smoothscale(surf, size) if size else surf
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size) if size else img

# Math helpers
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
