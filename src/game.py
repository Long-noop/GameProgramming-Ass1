import pygame, random, math
from config import W, H, screen, font, font_medium, font_large, holes
from fx import FX
from zombie import Zombie
from hammer import Hammer
from utils import load_best, save_best, is_better, draw_text, safe_load_sound, safe_img

#background
BACKGROUND_IMG = pygame.image.load("../assets/2-800x501.png").convert()
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (W, H))

#menu
MENU_BG_IMG = safe_img("../assets/menu.png", (350, 395))


SND_HIT  = safe_load_sound("../assets/hit.wav", 0.35)
SND_POP  = safe_load_sound("../assets/pop.mp3", 0.35)
SND_MISS = safe_load_sound("../assets/miss.mp3", 0.25)
SETTINGS_BTN_IMG = safe_img("../assets/setting-button.webp", (40, 40))
SETTINGS_BTN_RECT = SETTINGS_BTN_IMG.get_rect()
SETTINGS_BTN_RECT.topleft = (10, H-50) 
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
        self.paused_time = 0
        self.state = "playing"   # mặc định khởi động ở menu
        self.show_music = True   # setting: bật/tắt nhạc nền
        self.sound_hit_enabled = True # setting: bật/tắt âm thanh hit
        self.sound_btn = pygame.Rect(0,0,0,0)  # tạo trước để tránh AttributeError
        self.music_pos = 0  # lưu vị trí nhạc hiện tại

        # số lần miss tối đa
        self.max_miss = 6 # có thể chỉnh sửa

        self.btn_rect = pygame.Rect(250, 280, 200, 50)
        self.best = load_best()     # tải kỷ lục hiện có
        self.saved_best = False
        self.reset()

    # def toggle_music(self):
    #     self.show_music = not self.show_music
    #     try:
    #         if self.show_music:
    #             pygame.mixer.music.play(-1)
    #             pygame.mixer.music.set_volume(0.4)
    #         else:
    #             pygame.mixer.music.stop()
    #     except Exception:
    #         pass
    def toggle_music(self):
        self.show_music = not self.show_music
        try:
            if self.show_music:
                # play tiếp tục từ vị trí cũ
                pygame.mixer.music.play(-1, start=self.music_pos)
                pygame.mixer.music.set_volume(0.4)
            else:
                # lưu vị trí hiện tại trước khi pause
                self.music_pos += pygame.mixer.music.get_pos() / 1000  # milliseconds -> seconds
                pygame.mixer.music.stop()
        except Exception:
            pass

    def on_click(self, mx, my):
        if self.state == "playing":
            if SETTINGS_BTN_RECT.collidepoint((mx,my)):
                self.paused_time = self.game_end_time - pygame.time.get_ticks()
                self.state = "settings"
                return
            self.hammer.start()
            _ = self.try_hit(mx, my)

        elif self.state == "game_over":
            if self.btn_rect.collidepoint((mx,my)):
                self.reset()
            elif SETTINGS_BTN_RECT.collidepoint((mx,my)):
                self.state = "settings"

        elif self.state == "settings":
            if self.music_btn.collidepoint((mx,my)):
                self.toggle_music()
            elif self.sound_btn.collidepoint((mx,my)):
                self.sound_hit_enabled = not self.sound_hit_enabled
            elif self.back_btn.collidepoint((mx,my)) or self.back_btn1.collidepoint((mx,my)):
                self.game_end_time = pygame.time.get_ticks() + self.paused_time
                self.state = "playing"
            elif self.end_btn.collidepoint((mx,my)):
                self.state = "game_over"

    def draw_settings(self):
        # Overlay mờ toàn màn hình
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Popup menu dùng hình nền
        popup = MENU_BG_IMG.get_rect(center=(W//2, H//2))
        screen.blit(MENU_BG_IMG, popup)  # dùng ảnh nền menu

        # Tọa độ trung tâm popup
        cx = popup.centerx

        # Các nút invisible (vẫn click được)
        self.back_btn = pygame.Rect(cx-100, 100, 200, 60)
        self.back_btn1 = pygame.Rect(cx+120, 50, 50, 50)
        self.music_btn  = pygame.Rect(popup.left + 180, popup.bottom-110, 60, 50)
        self.end_btn   = pygame.Rect(cx-100, 170, 200, 60)
        self.sound_btn  = pygame.Rect(popup.left + 95, popup.bottom-110, 60, 50)
        if not self.show_music:
            pygame.draw.line(screen, (255,0,0), 
                (self.music_btn.left+5, self.music_btn.top+5),
                (self.music_btn.right-5, self.music_btn.bottom-5), 4)
        if not self.sound_hit_enabled:
            pygame.draw.line(screen, (255,0,0), 
                (self.sound_btn.left, self.sound_btn.top+5),
                (self.sound_btn.right, self.sound_btn.bottom-5), 4)
    def current_acc(self):
        total = self.hit + self.miss
        return int(self.hit/total*100) if total>0 else 0

    def maybe_update_best(self):
        new = {"hit": self.hit, "acc": self.current_acc()}
        if is_better(new, self.best):
            save_best(new)
            self.best = new
            self.saved_best = True

    def reset(self):
        now = pygame.time.get_ticks()
        self.hit = self.miss = self.combo = 0
        self.combo_time = now
        self.zombies.clear()
        self.wave_timer = now + 1200
        self.game_end_time = now + 60000
        self.state = "playing"
        self.saved_best = False

    def spawn_wave(self):
        self.zombies.clear()
        n = random.choices([1,2,3], weights=[0.55,0.33,0.12], k=1)[0]
        types = ["normal", "black", "gold"] # danh sách loại zombie
        for pos in random.sample(holes, k=n):
              ztype = random.choices(types, weights=[0.7, 0.2, 0.1])[0]
              self.zombies.append(Zombie(pos, ztype))
        if SND_POP: SND_POP.play()

    def try_hit(self, mx, my):
        for z in reversed(self.zombies):
            if z.try_hit(mx, my):
            # điểm hit theo loại zombie
                if z.ztype == "gold":
                    self.hit += 2
                    label, col = "Jackpot!", (255, 215, 0)
                elif z.ztype == "black":
                    self.hit = max(0, self.hit - 1)
                    label, col = "Oops!", (50,50,50)
                else:
                    self.hit += 1
                # zombie normal: tùy khoảng cách
                    zx, zy = z.base[0], z.base[1] + int(z.y_offset)
                    dist = math.hypot(mx - zx, my - zy)
                    if dist <= 18:
                        label, col = "Perfect!", (255, 240, 120)
                    else:
                        label, col = "Great!", (120, 220, 120)
                 # combo
                self.combo += 1
                self.combo_time = pygame.time.get_ticks()
                # âm thanh & FX
                if self.sound_hit_enabled and SND_HIT:
                    SND_HIT.play()
                self.fx.hitstop(65)
                self.fx.shake(6, 110)
                self.fx.spawn_particles(z.base, (210,40,40), count=14, speed=2.5)
                 # chữ nổi
                self.fx.add_text(label, (z.base[0], z.base[1]-35), color=col, life=750)
                return True   #  trả về ngay khi trúng zombie


        # MISS (chỉ chạy khi không trúng zombie nào)
        self.miss += 1  
        self.combo = 0
        if SND_MISS: SND_MISS.play()
        self.fx.shake(3, 60)
        self.fx.spawn_dust((mx, my), count=12, speed=3.0)
        self.fx.spawn_crack((mx, my), branches=5, length_rng=(16, 34), life=1400)
        self.fx.add_text("Miss!", (mx, my - 30), color=(255,80,80), life=900)

        # ===== Kiểm tra Game Over vì Miss =====
        if self.miss >= self.max_miss:
             self.state = "game_over"
        if not self.saved_best:
            self.maybe_update_best()
        return False
    
    def register_escape_miss(self, z):
        # zombie black tự chìm => trừ 1 hit
        # if z.ztype == "black":
        #     self.hit = max(0, self.hit - 1)
        # else:
        #     self.miss += 1
        if z.ztype != "black":
            self.miss += 1

            self.combo = 0
            if SND_MISS: SND_MISS.play()
            base = (z.base[0], z.base[1] + 28)
            self.fx.spawn_dust(base, count=16, speed=2.4)
            self.fx.spawn_crack(base, branches=6, length_rng=(20, 42), life=1700)
            self.fx.add_text("Miss!", (z.base[0], z.base[1]-30), color=(255,80,80), life=900)
            self.fx.shake(3, 60)

        # ===== Kiểm tra Game Over vì Miss =====
        if self.miss >= self.max_miss:
            self.state = "game_over"
            if not self.saved_best:
                self.maybe_update_best()

    # def on_click(self, mx, my):
    #     if self.state == "playing":
    #         self.hammer.start()
    #         _ = self.try_hit(mx, my)
    #     elif self.state == "game_over":
    #         if self.btn_rect.collidepoint((mx,my)):
    #             self.reset()

    def update(self, dt):
        self.fx.update(dt)
        if self.state in ("settings", "game_over"):
            return
        if self.fx.hitstop_timer > 0:
            return

        now = pygame.time.get_ticks()
        if now >= self.game_end_time:
            self.state = "game_over"
            if not self.saved_best:
                self.maybe_update_best()
            return

        if now > self.wave_timer and not self.zombies:
            self.spawn_wave()
            self.wave_timer = now + 1500

        alive = []
        for z in self.zombies:
            still = z.update(dt)
            if still:
                alive.append(z)
            else:
                # Zombie biến mất: nếu chưa bị hit => tính miss (escape)
                if not z.hit:
                    self.register_escape_miss(z)
        self.zombies = alive

        self.hammer.update()

    def draw_world(self):
        screen.blit(BACKGROUND_IMG, (0, 0))
        for pos in holes:
            pygame.draw.circle(screen, (90, 60, 20), pos, 50)

        # Vẽ zombie
        for z in self.zombies:
            z.draw(screen)

        # FX
        self.fx.draw_particles()
        self.fx.draw_cracks(screen)
        self.fx.draw_floating_texts(screen)

        # HUD
        now = pygame.time.get_ticks()
        time_left = max(0, (self.game_end_time - now)//1000)
        draw_text(f"Time: {time_left}", font, (255,255,255), W-160, 10)
        draw_text(f"Hit: {self.hit}", font, (255,255,255), 10, 10)
        draw_text(f"Miss: {self.miss}", font, (255,255,255), 10, 40)
        acc = self.current_acc()
        draw_text(f"Acc: {acc}%", font, (255,255,255), 10, 70)

        if self.combo >= 2:
            draw_text(f"COMBO x{self.combo}", font_medium, (255,255,255), W//2, 20, center=True)

    def draw_game_over(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0,0,0,150))
        screen.blit(s, (0,0))

        popup_rect = pygame.Rect(150, 50, 400, 320)
        pygame.draw.rect(screen, (45,52,71), popup_rect, border_radius=15)
        cx = popup_rect.centerx

        draw_text("Time's Up!", font_large, (255,223,0), cx, 100, center=True)
        draw_text(f"Hits: {self.hit}", font_medium, (255,255,255), cx, 165, center=True)
        draw_text(f"Misses: {self.miss}", font_medium, (255,255,255), cx, 205, center=True)
        acc = self.current_acc()
        draw_text(f"Accuracy: {acc}%", font_medium, (255,255,255), cx, 245, center=True)

        # Kỷ lục
        if self.best:
            draw_text(f"Best: {self.best['acc']}% | {self.best['hit']} hits", font, (255,255,255), cx, 275, center=True)
        else:
            draw_text("Best: --", font, (200,200,200), cx, 275, center=True)

        self.btn_rect.centerx = cx
        self.btn_rect.y = 310
        pygame.draw.rect(screen, (0,177,64), self.btn_rect, border_radius=10)
        draw_text("Tap to try again", font, (255,255,255),
                  self.btn_rect.centerx, self.btn_rect.centery, center=True)

    def draw(self, mx, my):
        ox, oy = self.fx.offset()
        if self.state in ("playing", "game_over"):
            self.draw_world()
            if self.state == "game_over":
                self.draw_game_over()
            self.hammer.draw(mx, my)

            screen.blit(SETTINGS_BTN_IMG, SETTINGS_BTN_RECT)

        elif self.state == "settings":
            self.draw_settings() 

        # FX shake
        if ox or oy:
            frame = screen.copy()
            screen.fill((46,168,82))
            screen.blit(frame, (int(ox), int(oy)))
