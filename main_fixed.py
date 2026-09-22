# main.py
import sys
import math
import pygame

from levels import LEVELS, LEVEL_ORDER

# ---------------- 基础配置 ----------------
WIDTH, HEIGHT = 720, 720
FPS = 60

CELL = 80
BOARD_LEFT = 60
BOARD_TOP = 140

# ========= Dimoo 梦境主题 =========

BG_COLOR = (235, 230, 250)

BOARD_BG = (255, 250, 255)

GRID_LINE = (225, 215, 240)


TEXT_COLOR = (90,70,120)

SUBTEXT_COLOR = (150,130,170)


ARROW_COLOR = (170,130,255)

ARROW_BAD_COLOR = (255,120,150)


BTN_BG = (180,150,255)

BTN_BG_HOVER = (210,180,255)

BTN_TEXT = (255,255,255)

OVERLAY = (255, 255, 255, 235)

# ===== Dimoo 梦境增强元素 =====
CLOUD_COLOR = (255, 255, 255)
CLOUD_SHADOW = (230, 220, 250)
CHAR_FACE = (250, 225, 235)
CHAR_EYE = (90, 80, 130)
CHAR_CHEEK = (255, 160, 190)
GLOW_COLOR = (235, 210, 255)


UP, DOWN, LEFT, RIGHT = 1, 2, 3, 4

# 逻辑方向： (行增量, 列增量)
DIR_VEC = {
    UP:    (-1, 0),
    DOWN:  ( 1, 0),
    LEFT:  ( 0, -1),
    RIGHT: ( 0, 1),
}

STATE_START = "start"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_LOSE = "lose"

DEBUG = True  # 打开后，点击会打印坐标与判定信息


# ---------------- 工具函数 ----------------
def draw_dream_background(surface):

    surface.fill(BG_COLOR)

    stars=[
        (80,90),
        (180,60),
        (600,120),
        (650,500),
        (100,580),
        (550,650)
    ]

    t = pygame.time.get_ticks()/500

    for i,(x,y) in enumerate(stars):

        size = 3 + int(
            abs(math.sin(t+i))*3
        )

        pygame.draw.circle(
            surface,
            (255,230,180),
            (x,y),
            size
        )


def draw_cloud(surface, x, y):
    """绘制梦境云朵装饰"""
    pygame.draw.circle(surface, CLOUD_SHADOW, (x+5, y+8), 34)
    pygame.draw.circle(surface, CLOUD_COLOR, (x, y), 32)
    pygame.draw.circle(surface, CLOUD_COLOR, (x+35, y-12), 42)
    pygame.draw.circle(surface, CLOUD_COLOR, (x+70, y), 30)
    pygame.draw.rect(surface, CLOUD_COLOR, (x, y, 70, 28))


def draw_dream_character(surface, x, y):
    """自主绘制的梦境精灵装饰"""
    pygame.draw.circle(surface, CHAR_FACE, (x, y), 35)

    pygame.draw.circle(surface, CHAR_EYE, (x-12, y-5), 6)
    pygame.draw.circle(surface, CHAR_EYE, (x+12, y-5), 6)

    pygame.draw.circle(surface, CHAR_CHEEK, (x-22, y+12), 6)
    pygame.draw.circle(surface, CHAR_CHEEK, (x+22, y+12), 6)


def draw_text(surface, text, font, color, center=None, topleft=None):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    surface.blit(img, rect)
    return rect


def make_arrow_points(cx, cy, direction, size, scale=1):
    """返回三角形三个顶点。"""
    size = int(size * scale)

    head=size
    tail = size * 0.62

    if direction == UP:
        return [(cx, cy - head), (cx - tail, cy + tail), (cx + tail, cy + tail)]
    if direction == DOWN:
        return [(cx, cy + head), (cx - tail, cy - tail), (cx + tail, cy - tail)]
    if direction == LEFT:
        return [(cx - head, cy), (cx + tail, cy - tail), (cx + tail, cy + tail)]
    if direction == RIGHT:
        return [(cx + head, cy), (cx - tail, cy - tail), (cx - tail, cy + tail)]
    return None


def draw_arrow(
    surface,
    center,
    direction,
    color,
    size=26,
    border=True,
    scale=1
):
    pts = make_arrow_points(center[0], center[1], direction, size, scale)
    if not pts:
        return
    # 外层柔光
    glow_pts = make_arrow_points(center[0], center[1], direction, size + 8, scale)
    if glow_pts:
        pygame.draw.polygon(surface, GLOW_COLOR, glow_pts)

    pygame.draw.polygon(surface, color, pts)

    if border:
        pygame.draw.polygon(surface, (255, 255, 255), pts, 2)


# ---------------- 按钮 ----------------
class Button:
    def __init__(self, rect, text, font, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.hover = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

    def draw(self, surface):
        color = BTN_BG_HOVER if self.hover else BTN_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        draw_text(surface, self.text, self.font, BTN_TEXT, center=self.rect.center)


# ---------------- 飞出动画 ----------------
class FlyAnimation:
    def __init__(self, row, col, direction, start_rect, duration=0.28):
        self.row = row
        self.col = col
        self.direction = direction
        self.start_rect = pygame.Rect(start_rect)
        self.duration = duration
        self.t = 0.0
        self.finished = False

    def update(self, dt):
        self.t += dt
        if self.t >= self.duration:
            self.finished = True

    def draw(self, surface):
        progress = min(self.t / self.duration, 1.0)
        ease = 1 - (1 - progress) ** 3
        dist = 560 * ease

        # 逻辑方向 (dr, dc) 转成屏幕偏移 (dx, dy)
        dr, dc = DIR_VEC[self.direction]
        offset = (dc * dist, dr * dist)

        alpha = int(255 * (1 - progress))

        temp = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        pts = make_arrow_points(CELL // 2, CELL // 2, self.direction, 26, 1)
        if pts:
            pygame.draw.polygon(temp, (*ARROW_COLOR, alpha), pts)

        surface.blit(
            temp,
            (self.start_rect.x + offset[0], self.start_rect.y + offset[1]),
        )


# ---------------- 游戏主类 ----------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("一箭又一箭")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("microsoftyahei,simhei,arial", 48, bold=True)
        self.font_mid = pygame.font.SysFont("microsoftyahei,simhei,arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("microsoftyahei,simhei,arial", 18)

        self.state = STATE_START
        self.level_index = 0

        self.grid = []
        self.rows = 0
        self.cols = 0
        self.max_mistakes = 0
        self.mistakes_left = 0

        self.fly_animations = []
        self.bad_effects = {}
        self.animating_cells = set()  # 正在飞出，逻辑上仍算有箭头

        self.restart_button = Button(
            (WIDTH - 170, 32, 130, 46),
            "重新开始",
            self.font_small,
            self.restart_level,
        )

        self.win_button = None
        self.lose_button = None
        self.start_button_rect = pygame.Rect(WIDTH // 2 - 110, 420, 220, 64)

        self.load_level(0, enter_playing=False)

    # ---------- 关卡管理 ----------
    def load_level(self, index, enter_playing=True):
        self.level_index = index
        data = LEVELS[LEVEL_ORDER[index]]

        self.grid = [row[:] for row in data["grid"]]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows else 0
        self.max_mistakes = data["mistakes"]
        self.mistakes_left = self.max_mistakes

        self.fly_animations.clear()
        self.bad_effects.clear()
        self.animating_cells.clear()
        self.win_button = None
        self.lose_button = None

        if enter_playing:
            self.state = STATE_PLAYING

    def restart_level(self):
        self.load_level(self.level_index, enter_playing=True)

    def start_game(self):
        self.load_level(0, enter_playing=True)

    def go_start(self):
        self.state = STATE_START

    def next_level(self):
        if self.level_index + 1 < len(LEVEL_ORDER):
            self.load_level(self.level_index + 1, enter_playing=True)
        else:
            self.go_start()

    # ---------- 棋盘逻辑 ----------
    def cell_rect(self, row, col):
        return pygame.Rect(
            BOARD_LEFT + col * CELL,
            BOARD_TOP + row * CELL,
            CELL,
            CELL,
        )

    def count_arrows(self):
        n = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != 0:
                    n += 1
        return n

    def is_blocked(self, row, col):
        """路径上是否有箭头。正在飞出的箭头仍算有箭头。"""
        direction = self.grid[row][col]
        if direction == 0:
            return True

        dr, dc = DIR_VEC[direction]
        r, c = row + dr, col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols:
            if self.grid[r][c] != 0:
                return True
            r += dr
            c += dc
        return False

    def debug_blockers(self, row, col):
        direction = self.grid[row][col]
        dr, dc = DIR_VEC[direction]
        r, c = row + dr, col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols:
            if self.grid[r][c] != 0:
                print(f"    被 ({r},{c}) 挡住，值={self.grid[r][c]}")
                return
            r += dr
            c += dc
        print("    路径上没有箭头（不应该发生）")

    def handle_click_arrow(self, row, col):
        if self.state != STATE_PLAYING:
            return
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if self.grid[row][col] == 0:
            return
        if (row, col) in self.animating_cells:
            return

        direction = self.grid[row][col]

        if self.is_blocked(row, col):
            if DEBUG:
                print(f"[失误] ({row},{col}) 方向={direction} 被挡住")
                self.debug_blockers(row, col)
            self.mistakes_left -= 1
            self.bad_effects[(row, col)] = 0.45
            if self.mistakes_left <= 0:
                self.mistakes_left = 0
                self.state = STATE_LOSE
                self.lose_button = Button(
                    (WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 56),
                    "重新开始",
                    self.font_mid,
                    self.restart_level,
                )
        else:
            if DEBUG:
                print(f"[飞出] ({row},{col}) 方向={direction}")
            rect = self.cell_rect(row, col)
            self.fly_animations.append(FlyAnimation(row, col, direction, rect))
            self.animating_cells.add((row, col))
            # 注意：这里不把 grid 置 0，等动画结束再置 0

    # ---------- 事件 ----------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == STATE_START:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        self.start_game()
                continue

            if self.state == STATE_PLAYING:
                if self.restart_button.handle_event(event):
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if (BOARD_LEFT <= mx < BOARD_LEFT + self.cols * CELL and
                            BOARD_TOP <= my < BOARD_TOP + self.rows * CELL):
                        col = (mx - BOARD_LEFT) // CELL
                        row = (my - BOARD_TOP) // CELL
                        if DEBUG:
                            print(f"[点击] 像素=({mx},{my}) -> 格子=({row},{col}) "
                                  f"值={self.grid[row][col]}")
                        self.handle_click_arrow(row, col)

            elif self.state == STATE_WIN:
                if self.win_button:
                    self.win_button.handle_event(event)

            elif self.state == STATE_LOSE:
                if self.lose_button:
                    self.lose_button.handle_event(event)

    # ---------- 更新 ----------
    def update(self, dt):
        for anim in self.fly_animations:
            anim.update(dt)

        finished = [a for a in self.fly_animations if a.finished]
        for a in finished:
            self.animating_cells.discard((a.row, a.col))
            self.grid[a.row][a.col] = 0  # 动画结束，逻辑上真正移除
        self.fly_animations = [a for a in self.fly_animations if not a.finished]

        for key in list(self.bad_effects.keys()):
            self.bad_effects[key] -= dt
            if self.bad_effects[key] <= 0:
                del self.bad_effects[key]

        if self.state == STATE_PLAYING:
            if self.count_arrows() == 0 and not self.fly_animations:
                self.state = STATE_WIN
                if self.level_index + 1 < len(LEVEL_ORDER):
                    text = "下一关"
                    cb = self.next_level
                else:
                    text = "返回开始"
                    cb = self.go_start
                self.win_button = Button(
                    (WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 56),
                    text,
                    self.font_mid,
                    cb,
                )

    # ---------- 绘制 ----------
    def draw_hud(self):
        pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, WIDTH, 110))
        pygame.draw.line(self.screen, GRID_LINE, (0, 110), (WIDTH, 110), 2)

        draw_text(self.screen, f"关卡 {self.level_index + 1} / {len(LEVEL_ORDER)}",
                  self.font_mid, TEXT_COLOR, topleft=(30, 24))
        draw_text(self.screen, f"剩余箭头：{self.count_arrows()}",
                  self.font_small, SUBTEXT_COLOR, topleft=(30, 66))
        draw_text(self.screen, f"剩余失误：{self.mistakes_left} / {self.max_mistakes}",
                  self.font_small, SUBTEXT_COLOR, topleft=(220, 66))

        self.restart_button.draw(self.screen)

    def draw_board(self):
        board_rect = pygame.Rect(
            BOARD_LEFT - 6, BOARD_TOP - 6,
            self.cols * CELL + 12, self.rows * CELL + 12,
        )
        pygame.draw.rect(self.screen, BOARD_BG, board_rect, border_radius=14)
        pygame.draw.rect(self.screen, GRID_LINE, board_rect, 2, border_radius=14)

        for r in range(self.rows + 1):
            y = BOARD_TOP + r * CELL
            pygame.draw.line(self.screen, GRID_LINE,
                             (BOARD_LEFT, y),
                             (BOARD_LEFT + self.cols * CELL, y), 2)
        for c in range(self.cols + 1):
            x = BOARD_LEFT + c * CELL
            pygame.draw.line(self.screen, GRID_LINE,
                             (x, BOARD_TOP),
                             (x, BOARD_TOP + self.rows * CELL), 2)

        for r in range(self.rows):
            for c in range(self.cols):
                direction = self.grid[r][c]
                if direction == 0:
                    continue
                if (r, c) in self.animating_cells:
                    continue  # 正在飞的用动画画

                rect = self.cell_rect(r, c)
                center = rect.center

                if (r, c) in self.bad_effects:
                    t = self.bad_effects[(r, c)]
                    offset_x = math.sin(t * 60) * 6
                    draw_arrow(self.screen, (center[0] + offset_x, center[1]),
                               direction, ARROW_BAD_COLOR)
                else:
                    draw_arrow(self.screen, center, direction, ARROW_COLOR)

        for anim in self.fly_animations:
            anim.draw(self.screen)

    def draw_start(self):
        draw_dream_background(self.screen)
        draw_text(self.screen, "一箭又一箭", self.font_title, TEXT_COLOR,
                  center=(WIDTH // 2, 220))
        draw_text(self.screen, "点击箭头，若它朝向的路径上没有其他箭头，就会飞出。",
                  self.font_small, SUBTEXT_COLOR, center=(WIDTH // 2, 300))
        draw_text(self.screen, "被挡住就会失误，失误耗尽则失败。",
                  self.font_small, SUBTEXT_COLOR, center=(WIDTH // 2, 330))

        mouse = pygame.mouse.get_pos()
        hover = self.start_button_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, BTN_BG_HOVER if hover else BTN_BG,
                         self.start_button_rect, border_radius=14)
        draw_text(self.screen, "开始游戏", self.font_mid, BTN_TEXT,
                  center=self.start_button_rect.center)
        draw_text(self.screen, "点击任意位置开始", self.font_small, SUBTEXT_COLOR,
                  center=(WIDTH // 2, 520))

    def draw_win(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, "通关！", self.font_title, (34, 160, 90),
                  center=(WIDTH // 2, HEIGHT // 2 - 80))
        draw_text(self.screen, f"你完成了第 {self.level_index + 1} 关",
                  self.font_mid, TEXT_COLOR, center=(WIDTH // 2, HEIGHT // 2 - 10))
        if self.win_button:
            self.win_button.draw(self.screen)

    def draw_lose(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, "失败", self.font_title, (220, 60, 60),
                  center=(WIDTH // 2, HEIGHT // 2 - 80))
        draw_text(self.screen, "失误次数已耗尽", self.font_mid, TEXT_COLOR,
                  center=(WIDTH // 2, HEIGHT // 2 - 10))
        if self.lose_button:
            self.lose_button.draw(self.screen)

    def draw(self):
        if self.state == STATE_START:
            self.draw_start()
            return
        self.screen.fill(BG_COLOR)

        # 梦境装饰
        draw_cloud(self.screen, 25, 330)
        draw_cloud(self.screen, 590, 330)

        draw_dream_character(
            self.screen,
            55,
            620
        )

        draw_dream_character(
            self.screen,
            665,
            620
        )

        self.draw_hud()
        self.draw_board()
        if self.state == STATE_WIN:
            self.draw_win()
        elif self.state == STATE_LOSE:
            self.draw_lose()

    # ---------- 主循环 ----------
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
