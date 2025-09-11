import os, json, pygame, sys
from config import screen, clock

RECORD_PATH = "best_record.json"
font_small = pygame.font.SysFont(None, 28)
font_medium = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 48)

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

def intro_screen():
    while True:
        screen.fill((30, 30, 60))
        draw_text("ZOMBIE WHACK!", font_large, (255, 200, 50), 180, 30)
        info_font = pygame.font.SysFont(None, 20)
        draw_text("!!! Game vay mượn hình ảnh, đồ họa từ tựa game huyền thoại Plants vs Zombies", info_font, (200, 255, 200), 100, 70)
        draw_text("Luật chơi:", font_medium, (200, 255, 200), 50, 120)
        draw_text("- Click chuột để dùng búa.", font_small, (255,255,255), 70, 160)
        draw_text("- Đập trúng zombie: Hit +1 hoặc +2 (tùy loại zombie).", font_small, (255,255,255), 70, 190)
        draw_text("- Đập hụt/ không đập: Miss +1.", font_small, (255,255,255), 70, 220)
        draw_text("- Đập trúng hoa: Hit -1.", font_small, (255,255,255), 70, 250)
        draw_text("Điểm số được tính = Hit/(Hit + Miss)", font_small, (255,255,255), 70, 280)
        draw_text("Thời gian: 60 giây", font_small, (255,255,255), 70, 310)
        
        draw_text("Ấn ENTER để bắt đầu!", font_medium, (255,100,100), 200, 350)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return  # thoát intro → vào game

        pygame.display.update()
