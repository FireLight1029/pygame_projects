import pygame
pygame.init()
import math, random
import numpy as np
import json, os

################################################################################
# VISUAL THEME
################################################################################

BG_DARK = (12, 14, 24)
PANEL = (26, 30, 48)
PANEL_BORDER = (90, 100, 180)
ACCENT = (120, 140, 255)
TEXT_MAIN = (235, 235, 245)
TEXT_DIM = (160, 170, 210)
SHADOW = (5, 6, 12)

COLORS = [
    (255, 60, 60),
    (60, 255, 60),
    (60, 120, 255),
    (255, 240, 60),
    (60, 255, 255),
    (255, 60, 255),
    (255, 160, 60),
    (255, 120, 180),
    (180, 255, 60),
    (160, 60, 255),
]

################################################################################
# POWERUPS
################################################################################

powerup_list = [
    "long_paddle",
    "slow_ball",
    "multiball",
    "sticky_paddle",
    "laser_paddle"
]

power_color = {
    "long_paddle" : (255, 60, 60),
    "slow_ball" : (60, 120, 255),
    "multiball" : (255, 240, 60),
    "sticky_paddle" : (255, 60, 255),
    "laser_paddle" : (180, 255, 60)
}

################################################################################
# UI HELPERS
################################################################################

def draw_panel(screen, rect, r=12):
    pygame.draw.rect(screen, SHADOW, rect.move(4,4), border_radius=r)
    pygame.draw.rect(screen, PANEL, rect, border_radius=r)
    pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=r)

################################################################################
# CLASSES
################################################################################

class Ball:
    def __init__(self, pos, vel, r=7):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.r = r
        self.px, self.py = pos
        self.stuck = False

    def update(self, dt):
        global pad
        if self.stuck:
            self.x = pad.x+pad.len//2
        self.px, self.py = self.x, self.y
        if self.x > W - self.r:
            self.vx *= -1
            self.x = W - self.r - 1
        if self.x < self.r:
            self.vx *= -1
            self.x = self.r + 1
        if self.y < self.r:
            self.vy *= -1
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.y > H - self.r

    def draw(self, screen):
        pygame.draw.circle(screen, (255,80,80), (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, (255,140,140), (int(self.x), int(self.y)), self.r, 1)

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, screen, use, font, hover=False, text_col=TEXT_MAIN):
        base = (80,100,200) if use=="lvl_menu" else (70,70,90)
        color = tuple(min(255,c+30) for c in base) if hover else base
        pygame.draw.rect(screen, SHADOW, self.rect.move(3,3), border_radius=10)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, ACCENT, self.rect, 2, border_radius=10)
        label = font.render(self.text, True, text_col)
        screen.blit(label, (
            self.rect.centerx - label.get_width()//2,
            self.rect.centery - label.get_height()//2
        ))

class Paddle:
    def __init__(self, pos, len=60):
        self.x = pos
        self.y = 440
        self.base_len = len
        self.len = len
        self.v = 0
        self.sticky = False
        self.update(0)

    def update(self, dt):
        self.x = max(self.len/2, min(W-self.len/2, self.x + self.v*dt))
        self.range = [self.x-self.len/2, self.x+self.len/2]
        self.rect = pygame.Rect(self.range[0], self.y-5, self.len, 10)

    def draw(self, screen):
        pygame.draw.rect(screen, SHADOW, self.rect.move(0,3), border_radius=6)
        pygame.draw.rect(screen, ACCENT, self.rect, border_radius=6)

class PowerUps:
    def __init__(self, pos):
        self.x, self.y = pos
        self.type = random.choice(list(powerup_list))
        self.color = power_color[self.type]
        self.active = True
        self.rect = pygame.Rect(self.x, self.y, 20, 20)

    def update(self, dt):
        self.y += 80*dt
        self.rect.topleft = (self.x, self.y)
        if self.y > H: self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, SHADOW, self.rect.move(2,2), border_radius=6)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)

class Laser:
    def __init__(self, pos):
        self.x, self.y = pos
        self.vy = -400
        self.active = True
        self.rect = pygame.Rect(self.x-1, self.y, 2, 8)

    def update(self, dt):
        self.y += self.vy*dt
        self.rect.y = self.y
        if self.y < 0: self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, (255,80,80), self.rect)

################################################################################
# GAME HELPERS
################################################################################

def apply_powerup(type):
    global active_effects, ball_speed
    durations = {"long_paddle":20,"slow_ball":6,"sticky_paddle":10,"laser_paddle":5}
    if type!="multiball": active_effects[type]=durations[type]
    if type=="long_paddle": pad.len+=20
    if type=="slow_ball":
        ball_speed*=0.6
        for b in balls: b.vx*=0.6; b.vy*=0.6
    if type=="multiball":
        for b in balls[:]:
            ang=math.atan2(b.vy,b.vx)
            sp=math.hypot(b.vx,b.vy)
            for da in(-0.3,0.3):
                balls.append(Ball((b.x,b.y),(sp*math.cos(ang+da),sp*math.sin(ang+da))))
    if type=="sticky_paddle": pad.sticky=True

def remove_powerup(type):
    global ball_speed
    if type=="long_paddle": pad.len=pad.base_len
    if type=="slow_ball": ball_speed=ball_speed_archive
    if type=="sticky_paddle": pad.sticky=False

def count_bricks(grid):
    return sum(1 for row in grid for c in row if c != 0)

def draw_bricks(screen, brick_rows, brick_cols, gridge):
    brick_w = W // brick_cols
    for r in range(brick_rows):
        for c in range(brick_cols):
            if gridge[r][c] == 0:
                continue
            cr = r - 10 if r > 9 else r
            bx = c * brick_w
            by = BRICK_TOP + r * BRICK_H
            pygame.draw.rect(screen, COLORS[cr], (bx, by, brick_w-1, BRICK_H-1))

def brick_collision(ball):
    global number_bricks, powerups
    ball_rect = pygame.Rect(
        ball.x - ball.r,
        ball.y - ball.r,
        ball.r * 2,
        ball.r * 2
    )
    ball_prev = pygame.Rect(
        ball.px - ball.r,
        ball.py - ball.r,
        ball.r * 2,
        ball.r * 2
    )
    for r in range(BRICK_ROWS):
        for c in range(BRICK_COLS):
            if bricks[r][c] == 0:
                continue

            bx = c * BRICK_W
            by = BRICK_TOP + r * BRICK_H
            brick_rect = pygame.Rect(bx, by, BRICK_W, BRICK_H)

            if not ball_rect.colliderect(brick_rect):
                continue

            if ball_prev.bottom <= brick_rect.top or ball_prev.top >= brick_rect.bottom:
                if ball_rect.bottom > brick_rect.top or ball_rect.top < brick_rect.bottom:
                    ball.vy *= -1 

            elif ball_prev.right <= brick_rect.left or ball_prev.left >= brick_rect.right:
                if ball_rect.right > brick_rect.left or ball_rect.left < brick_rect.right:
                    ball.vx *= -1 

            bricks[r][c] = 0
            number_bricks -= 1
            if random.random() < 0.2:
                px = brick_rect.x + BRICK_W//2
                py = brick_rect.y + BRICK_H//2
                powerups.append(PowerUps((px, py)))

            return

def collide(ball, pad):
    if ball.vy > 0:
        pad_left = pad.range[0]
        pad_right = pad.range[1]
        pad_top = pad.y - 5
        
        ball_bottom = ball.y + ball.r
        ball_left = ball.x - ball.r
        ball_right = ball.x + ball.r
        if ball_bottom >= pad_top -2 and ball_bottom <= pad_top + 12:
            if ball_right >= pad_left and ball_left <= pad_right:
                cx = pad.x
                offset = (ball.x - cx) / (pad.len/2)
                angle = offset * max_bounce_angle
                if pad.sticky:
                    ball.vx = 0
                    ball.vy = 0
                    ball.y = pad_top - ball.r + 1
                    ball.x = pad.x
                    ball.stuck = True
                else:
                    ball.vx = ball_speed * math.sin(angle)
                    ball.vy = -ball_speed * math.cos(angle)
                    ball.y = pad_top - ball.r - 1

def save_level(level_name):
    global state, button_list
    data = {
        "rows": row_sel,
        "cols": col_sel,
        "grid": grid
    }
    with open(f"block_levels/{level_name}.json", "w") as f:
        json.dump(data, f)
    button_list = scan_lvls(level_dir)
    state = MENU

def scan_lvls(level_dir):
    contents = os.listdir(level_dir)
    numlvl = len(contents)    
    button_list = []
    margin = 30
    for i, lvl in enumerate(contents):
        name = lvl[:-5]
        
        rows, cols, grid = load_level(f"block_levels/{lvl}")
        preview = draw_preview_level(grid, rows, cols)
        
        temp = Button((30, 90 + (50*i), 180, 40), name)
        button_list.append({
            "name": name,
            "btn": temp,
            "preview":preview
        })
    return button_list

def load_level(path):
    with open(path, "r") as f:
        data = json.load(f)

    rows = data["rows"]
    cols = data["cols"]
    grid = data["grid"]

    return rows, cols, grid

def grid_initial(level_path):
    BRICK_ROWS, BRICK_COLS, bricks = load_level(level_path)
    return BRICK_ROWS, BRICK_COLS, bricks, W//BRICK_COLS

def draw_preview_level(grid, rows, cols, w = 100, h = 45):
    surf = pygame.Surface((w, h))
    surf.fill((0,0,0))
    cell_w = w//cols
    cell_h = h//rows
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                continue
            cr = r - 10 if r > 9 else r
            bx = c * cell_w
            by = r * cell_h
            pygame.draw.rect(surf, COLORS[cr], (bx, by, cell_w-1, cell_h-1))
    return surf

def clamp_level_scroll():
    global lvl_scroll

    total_height = len(button_list) * 55
    view_height = LVL_VIEW_BOTTOM - LVL_VIEW_TOP

    if total_height <= view_height:
        lvl_scroll = 8
        return

    max_scroll = 8
    min_scroll = view_height - total_height

    lvl_scroll = max(min(lvl_scroll, max_scroll), min_scroll)

################################################################################
#Start Menu
################################################################################

def events_menu(ev):
    global state, running
    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
        if start_btn.rect.collidepoint(ev.pos):
            state = LVL_SEL
        elif edit_btn.rect.collidepoint(ev.pos):
            state = GRD_SEL
        elif quit_btn.rect.collidepoint(ev.pos):
            running = False

def update_menu(dt):
    pass

def draw_menu(screen):
    screen.fill((0, 0, 0))
    title = font_big.render("BRICK BREAKER", True, (255, 255, 255))
    screen.blit(title, (W//2 - title.get_width()//2, 150))

    mx, my = pygame.mouse.get_pos()

    start_hover = start_btn.rect.collidepoint(mx, my)
    edit_hover = edit_btn.rect.collidepoint(mx, my)
    quit_hover  = quit_btn.rect.collidepoint(mx, my)

    start_btn.draw(screen, "start", font_small, start_hover)
    edit_btn.draw(screen, "start", font_small, edit_hover)
    quit_btn.draw(screen, "start", font_small, quit_hover)

################################################################################
#Game
################################################################################

def events_game(ev):
    global paused, state, balls, pad, game_over, game_win
    if game_over or game_win:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                state = LVL_SEL
                game_win = False
                game_over = False
                paused = True
                balls.clear()
                balls.append(Ball((320, 420), init_speed))
                powerups.clear()
                lasers.clear()
                for act in list(active_effects.keys()):
                    remove_powerup(act)
                    del active_effects[act]
                active_effects.clear()
                pad = Paddle(320)
    else:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                for ball in balls:
                    if ball.stuck:
                        ball.vx = ball_speed * math.sin(0.4)
                        ball.vy = -ball_speed * math.cos(0.4)
                        ball.stuck = False
                if "laser_paddle" in active_effects:
                    lasers.append(Laser((pad.range[0], pad.y)))
                    lasers.append(Laser((pad.range[1], pad.y)))
            if ev.key == pygame.K_ESCAPE:
                paused = not paused
            if ev.key == pygame.K_RIGHT:
                pad.v = pad_speed
            if ev.key == pygame.K_LEFT:
                pad.v = -pad_speed
            if game_win:
                if ev.key == pygame.K_SPACE:
                    state = LVL_SEL
        if ev.type == pygame.KEYUP:
            if ev.key == pygame.K_RIGHT:
                pad.v = 0
            if ev.key == pygame.K_LEFT:
                pad.v = 0

def update_game(dt):
    global game_over, game_win, powerups, active_effects, lasers
    if paused or game_over or game_win:
        return
    pad.update(dt)

    for i, ball in enumerate(balls):
        collide(ball, pad)
        brick_collision(ball)
        delball = ball.update(dt)
        if delball:
            balls.pop(i)
    for i, power in enumerate(powerups):
        power.update(dt)
        if power.rect.colliderect(pad.rect):
            apply_powerup(power.type)
            power.active = False
    powerups = [p for p in powerups if p.active]
    for act in list(active_effects.keys()):
        active_effects[act] -=dt
        if active_effects[act] <= 0:
            remove_powerup(act)
            del active_effects[act]
    for laser in lasers:
        laser.update(dt)
        for r in range(BRICK_ROWS):
            for c in range(BRICK_COLS):
                if bricks[r][c] == 0:
                    continue
                bx = c * BRICK_W
                by = BRICK_TOP + r * BRICK_H
                brick_rect = pygame.Rect(bx, by, BRICK_W, BRICK_H)
                if laser.rect.colliderect(brick_rect):
                    bricks[r][c] = 0
                    laser.active = False
                    break
    lasers = [l for l in lasers if l.active]
    if number_bricks == 0:
        game_win = True
    if len(balls) == 0:
        game_over = True

def draw_game(screen):
    screen.fill(BG_DARK)
    draw_bricks(screen, BRICK_ROWS, BRICK_COLS, bricks)
    for b in balls: b.draw(screen)
    pad.draw(screen)
    for p in powerups: p.draw(screen)
    for l in lasers: l.draw(screen)
    # PAUSED
    if paused and not (game_win or game_over):
        txt = font_big.render("PAUSED", True, TEXT_MAIN)
        sub = font_small.render("Press ESC to resume", True, TEXT_DIM)
        screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 40))
        screen.blit(sub, (W//2 - sub.get_width()//2, H//2 + 10))

    # GAME OVER
    if game_over:
        txt = font_big.render("GAME OVER", True, (255, 80, 80))
        sub = font_small.render("Press SPACE to return", True, TEXT_DIM)
        screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 40))
        screen.blit(sub, (W//2 - sub.get_width()//2, H//2 + 10))

    # WIN
    if game_win:
        txt = font_big.render("YOU WIN", True, TEXT_MAIN)
        sub = font_small.render("Press SPACE to continue", True, TEXT_DIM)
        screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - 40))
        screen.blit(sub, (W//2 - sub.get_width()//2, H//2 + 10))
################################################################################
#Grid Selection
################################################################################

def events_grd(ev):
    global col_sel, row_sel, state, grid
    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
        if minumcol.rect.collidepoint(ev.pos):
            if col_sel > 1:
                col_sel -= 1
        if minumrow.rect.collidepoint(ev.pos):
            if row_sel > 1:
                row_sel -= 1
        if pluslecol.rect.collidepoint(ev.pos):
            if col_sel < max_cols:
                col_sel += 1
        if pluslerow.rect.collidepoint(ev.pos):
            if row_sel < max_row:
                row_sel += 1
        if grid_sel.rect.collidepoint(ev.pos):
            grid = [[1 for _ in range(col_sel)] for _ in range(row_sel)]
            state = EDITOR
    if ev.type == pygame.KEYDOWN:
        if ev.key == pygame.K_ESCAPE:
            state = MENU

def update_grd(dt):
    pass

def draw_grd(screen):
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (40,40,40), (150, 160, 340, 190))
    bigfont = pygame.font.SysFont(None, 30)
    seldim = bigfont.render("Select dimentions", True, (250, 250, 250))
    screen.blit(seldim, (235, 180))
    smolfont = pygame.font.SysFont(None, 20)
    rowtxt = smolfont.render("Rows", True, (250, 250, 250))
    coltxt = smolfont.render("Cols", True, (250, 250, 250))
    screen.blit(rowtxt, (160, 228))
    pygame.draw.rect(screen, (150, 150, 150), (200, 230, 240, 10))
    screen.blit(coltxt, (160, 278))
    pygame.draw.rect(screen, (150, 150, 150), (200, 280, 240, 10))

    bar_len = 240
    bar_row = bar_len/max_row
    bar_col = bar_len/max_cols
    mean_bar = (bar_row + bar_col)//2
    pygame.draw.rect(screen, (250, 250, 250), ((200+(row_sel*(bar_row-1)), 225, mean_bar, 20)))
    rownum = smolfont.render(f"{row_sel}", True, (250, 250, 250))
    screen.blit(rownum, (460, 222))
    pygame.draw.rect(screen, (250, 250, 250), ((200+(col_sel*(bar_col-1)), 275, mean_bar, 20))) 
    colnum = smolfont.render(f"{col_sel}", True, (250, 250, 250))
    screen.blit(colnum, (460, 272))

    minumrow.draw(screen, "grid_sel", font_smol, text_col = (40, 40, 40))
    minumcol.draw(screen, "grid_sel", font_smol, text_col = (40, 40, 40))
    pluslecol.draw(screen, "grid_sel", font_smol, text_col = (40, 40, 40))
    pluslerow.draw(screen, "grid_sel", font_smol, text_col = (40, 40, 40))
    mx, my = pygame.mouse.get_pos()
    grid_hover = grid_sel.rect.collidepoint(mx, my)    
    grid_sel.draw(screen, "grid_sel", font_smol, text_col = (40, 40, 40), hover=grid_hover)
    
################################################################################
#Grid Editor
################################################################################

def events_editor(ev):
    global grid, typing_name, level_name, state
    cell_width = W//col_sel
    cell_height = BRICK_H
    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
        mx, my = pygame.mouse.get_pos()
        cellcol = mx // cell_width
        cellrow = (my-BRICK_TOP) // cell_height
        try:
            grid[cellrow][cellcol] = 0 if grid[cellrow][cellcol] == 1 else 1
        except:
            pass    
        if save_grid.rect.collidepoint(ev.pos):
            typing_name = True

    if ev.type == pygame.KEYDOWN:
        if ev.key == pygame.K_ESCAPE:
            state = GRD_SEL
        if typing_name:
            if ev.key == pygame.K_RETURN:
                if level_name:
                    save_level(level_name)
                    typing_name = False
            elif ev.key == pygame.K_BACKSPACE:
                level_name = level_name[:-1]
            elif ev.key == pygame.K_SPACE:
                level_name += "_"
            else:
                if ev.unicode.isalnum() or ev.unicode == "_":
                    level_name += ev.unicode

def update_editor(dt):
    pass

def draw_editor(screen):
    screen.fill((0,0,0))
    draw_bricks(screen, row_sel, col_sel, grid)
    mx, my = pygame.mouse.get_pos()
    save_hover = save_grid.rect.collidepoint(mx, my)
    save_grid.draw(screen, use = "grid_sel", font = font_small, hover= save_hover)
    #printing the name
    box = pygame.Rect(180, 340, 280, 40)
    pygame.draw.rect(screen, (40, 40, 40), box)
    pygame.draw.rect(screen, (200, 200, 200), box, 2)

    text = font_small.render(level_name or "Enter level name...", True, (255,255,255))
    screen.blit(text, (box.x + 8, box.y + 8))

################################################################################
#Level Selection Menu
################################################################################

def events_lvlsel(ev):
    global level_path, BRICK_ROWS, BRICK_COLS, bricks, BRICK_W, state, number_bricks, lvl_scroll
    if ev.type == pygame.MOUSEWHEEL:
        lvl_scroll += ev.y * LVL_SCROLL_SPEED
        clamp_level_scroll()

    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
        for button in button_list:
            if button["btn"].rect.collidepoint(ev.pos):
                level_path = f"{level_dir}{button['btn'].text}.json"
                BRICK_ROWS, BRICK_COLS, bricks, BRICK_W = grid_initial(level_path)
                number_bricks = count_bricks(bricks)
                state = GAME
    if ev.type == pygame.KEYDOWN:
        if ev.key == pygame.K_ESCAPE:
            state = MENU

def update_lvlsel(dt):
    pass

def draw_lvlsel(screen):
    screen.fill(BG_DARK)

    head = font_big.render("Select Level", True, TEXT_MAIN)
    screen.blit(head, (W//2 - head.get_width()//2, 30))

    # clip region (prevents drawing outside view)
    clip = pygame.Rect(0, LVL_VIEW_TOP, W, LVL_VIEW_BOTTOM - LVL_VIEW_TOP)
    screen.set_clip(clip)

    for i, button in enumerate(button_list):
        y = 90 + i * 55 + lvl_scroll

        if y < LVL_VIEW_TOP - 60 or y > LVL_VIEW_BOTTOM:
            continue

        btn = button["btn"]
        btn.rect.y = y

        card = pygame.Rect(btn.rect.x - 10, y - 6, 320, 52)
        draw_panel(screen, card, 10)

        mx, my = pygame.mouse.get_pos()
        hover = btn.rect.collidepoint(mx, my)
        btn.draw(screen, "lvl_menu", font_small, hover)

        screen.blit(button["preview"], (card.right - 110, y))

    screen.set_clip(None)

    hint = font_smol.render("Scroll to view more levels", True, TEXT_DIM)
    screen.blit(hint, (W//2 - hint.get_width()//2, H - 22))


level_dir = "block_levels/"
button_list = scan_lvls(level_dir)
################################################################################
#Code Start
################################################################################

game_win = False
game_over = False
paused = True
W, H = 640, 480
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

font_big = pygame.font.SysFont(None, 72)
font_small = pygame.font.SysFont(None, 32)
font_smol = pygame.font.SysFont(None, 20)

MENU = 0
LVL_SEL = 1
GAME = 2
GRD_SEL = 3
EDITOR = 4
state = MENU

#grid initialization
level_path = "block_levels/level_01.json"
BRICK_H = 20
BRICK_TOP = 30
BRICK_ROWS, BRICK_COLS, bricks, BRICK_W = grid_initial(level_path)

#main menu initiation
start_btn = Button((W//2 - 100, 250, 200, 50), "START")
edit_btn = Button((W//2 - 100, 320, 200, 50), "EDITOR")
quit_btn  = Button((W//2 - 100, 390, 200, 50), "QUIT")

#game initiation
ball_speed = 170 * 1.4
ball_speed_archive = ball_speed
pad_speed = 160 * 1.5
max_bounce_angle = math.radians(60)
init_speed = [ball_speed * math.sin(math.pi/4), -ball_speed * math.sin(math.pi/4)]
pad = Paddle(320)
balls = [Ball((320, 420), init_speed)]
number_bricks = 0

#level selector 
lvl_scroll = 8
LVL_SCROLL_SPEED = 40
LVL_VIEW_TOP = 90
LVL_VIEW_BOTTOM = H - 30

#powerups and storage
powerups = []
active_effects = {}
lasers = []

#grid selector initiation
max_row, max_cols = [15, 20]
init_row, init_col = [7, 10]
row_sel, col_sel = init_row, init_col
minumrow = Button((445, 235, 19, 19), "-")
pluslerow = Button((465, 235, 19, 19), "+")
minumcol = Button((445, 285, 19, 19), "-")
pluslecol = Button((465, 285, 19, 19), "+")
grid_sel = Button((270, 308, 100, 30), "Create Grid")
grid = []

#editor/ saving file
save_grid = Button((220, 400, 200, 50), "Save Grid")
level_name = ""
typing_name = False

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        
        if state == MENU:
            events_menu(ev)

        if state == LVL_SEL:
            events_lvlsel(ev)

        if state == GAME:
            events_game(ev)

        if state == GRD_SEL:
            events_grd(ev)

        if state == EDITOR:
            events_editor(ev)
    dt = clock.tick(60) / 1000.0
    
    if state == MENU:
        update_menu(dt)        
        draw_menu(screen)
    
    if state == LVL_SEL:
        update_lvlsel(dt)        
        draw_lvlsel(screen)
    
    if state == GAME:
        update_game(dt)
        draw_game(screen)

    if state == GRD_SEL:
        update_grd(dt)
        draw_grd(screen)

    if state == EDITOR:
        update_editor(dt)
        draw_editor(screen)
    
    pygame.display.flip()