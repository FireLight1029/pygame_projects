import pygame
pygame.init()
import math, random
import numpy as np

COLORS = [
    (255, 60, 60),    # red
    (60, 255, 60),    # green
    (60, 120, 255),   # blue
    (255, 240, 60),   # yellow
    (60, 255, 255),   # cyan
    (255, 60, 255),   # magenta
    (255, 160, 60),   # orange
    (255, 120, 180),  # pink
    (180, 255, 60),   # lime
    (160, 60, 255),   # purple
]

SHAPES = {
    '>':[[0,1],
         [1,1]],
    '.': [[1]],
    'I': [[1,1,1,1]],
    'O': [[1,1],
          [1,1]],
    'S': [[0,1,1],
          [1,1,0]],
    'Z': [[1,1,0],
          [0,1,1]],
    'T': [[0,1,0],
          [1,1,1]],
    'L': [[1,0],
          [1,0],
          [1,1]],
    'J': [[0,1],
          [0,1],
          [1,1]]
}
class block:
    def __init__(self, pos, color = (20, 20, 20)):
        self.x, self.y = pos
        self.color = color
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (((self.x)*CELL, (self.y)*CELL, CELL-2, CELL-2)), border_radius=2)

class piece:
    def __init__(self):
        self.type = random.choice(list(SHAPES.keys()))
        self.shape = [row[:] for row in SHAPES[self.type]]
        self.y = 0
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.color = random.choice(list(COLORS))
    def update(self):
        global grid
        # try to move piece down
        new_y = self.y + 1

        # bottom collision
        if collides(self, self.x, new_y, self.shape):
            return False
        
        self.y = new_y
        return True
    def colors(self, screen, blocks):
        for r, row in enumerate(self.shape):
            for c, val in enumerate(row):
                if val == 1:
                    blocks[self.y + r][self.x + c].color = self.color
                    #pygame.draw.rect(screen, (200, 50, 50), (((self.x+c)*CELL, (self.y+r)*CELL, CELL-1, CELL-1)))
    def copy(self):
        new = piece()
        new.type = self.type
        new.shape = [row[:] for row in self.shape]
        new.y = self.y
        new.x = self.x
        new.color = self.color
        return new

def next_draw(new, screen):
    pygame.draw.rect(screen, (20,20,20), ((170, 610, 120, 90)))
    size = 20
    new.x = 230 - (len(new.shape[0]) // 2)*size
    new.y = 655 - (len(new.shape) // 2)*size 
    
    for r, row in enumerate(new.shape):
        for c, val in enumerate(row):
            if val == 1:
                pygame.draw.rect(screen, new.color, (((new.x+c*size), (new.y+r*size), size-1, size-1)), border_radius=2)

def commit_piece(piece, grid):
    color = piece.color
    for r, row in enumerate(piece.shape):
        for c, val in enumerate(row):
            if val == 1:
                grid[piece.y + r][piece.x + c] = color
def move_piece(piece, dx):
    new_x = piece.x + dx
    if not collides(piece, new_x, piece.y, piece.shape):
        piece.x = new_x
def soft_drop(piece):
    new_y = piece.y + 1
    if not collides(piece, piece.x, new_y, piece.shape):
        piece.y = new_y
def rotate_piece(piece):
    rotated = np.rot90(piece.shape, k=-1).tolist()
    if not collides(piece, piece.x, piece.y, rotated):
        piece.shape = rotated
def grid_to_pixel(cell):
    r, c = cell
    return c * CELL, r * CELL

def collides(piece, new_x, new_y, shape):
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val == 1:
                nr = new_y + r
                nc = new_x + c

                if nr < 0 or nr >= ROWS: return True
                if nc < 0 or nc >= COLS: return True
                if grid[nr][nc] != 0: return True
    return False

def score_check(grid):
    full_rows = []

    for i, row in enumerate(grid):
        if all(cell != 0 for cell in row):
            full_rows.append(i)
    for i in full_rows:
        del grid[i]
        grid.insert(0, [0] * COLS)

    return len(full_rows)

W, H = 300, 600
CELL = 30
ROWS, COLS = H // CELL, W // CELL
blocks = [[block((c, r)) for c in range(COLS)] for r in range(ROWS)]

grid = [[0]*COLS for _ in range(ROWS)]
footer = 115
screen = pygame.display.set_mode((W, H + footer))
clock = pygame.time.Clock()

#global flags
timer = 0
game_speed = 2
move_delay = 1/ game_speed
running = True
paused = False
softtimer = 0
score = 0
keydown = False
game_over = False

pieces = [piece() for i in range(2)]
frozen = []
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                paused = not paused
            if ev.key == pygame.K_r:   # restart
                grid = [[0]*COLS for _ in range(ROWS)]
                pieces = [piece() for _ in range(2)]
                game_over = False
                score = 0
                gravity_timer = 0.0
            if not paused:
                if ev.key == pygame.K_LEFT:
                    move_piece(pieces[0], dx=-1)

                if ev.key == pygame.K_RIGHT:
                    move_piece(pieces[0], dx=1)

                if ev.key == pygame.K_DOWN:
                    keydown = True

                if ev.key == pygame.K_UP:
                    rotate_piece(pieces[0])
        if ev.type == pygame.KEYUP:
            if ev.key == pygame.K_DOWN:
                keydown = False
    screen.fill((0,0,0))
    font = pygame.font.SysFont(None, 50)
    title = font.render("TETRIS", True, (255, 255, 255))
    screen.blit(title, (20, H + 20))

    score_font = pygame.font.SysFont(None, 30)
    score_txt = score_font.render(f"Score: {score}", True, (200,200,200))
    screen.blit(score_txt, (20, H + 60))

    dt = clock.tick(30) / 1000.0
    next_piece = pieces[1].copy()
    next_draw(next_piece, screen)
    
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL
            y = r * CELL
            pygame.draw.rect(screen, (60, 60, 60), (x, y, CELL, CELL), width=1)
            if grid[r][c] == 0:
                blocks[r][c].color = (20,20,20)
            else:
                blocks[r][c].color = grid[r][c]
    pieces[0].colors(screen, blocks)

    if not paused and not game_over:
        timer += dt
        if timer > move_delay:
            timer -= move_delay
            moved = pieces[0].update()
            if not moved:
                # piece landed
                # freeze blocks and spawn next piece
                commit_piece(pieces[0], grid)
                pieces[0] = pieces[1]
                pieces[1] = piece()
                if collides(pieces[0], pieces[0].x, pieces[0].y, pieces[0].shape):
                    game_over = True
        complete_rows = score_check(grid)
        if complete_rows:
            score += 100 + 200* (complete_rows - 1)
        if keydown:
            soft_drop(pieces[0])
    
    for r in range(ROWS):
        for c in range(COLS):
            blocks[r][c].draw(screen)
    if paused:
        font = pygame.font.SysFont(None, 40)
        text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, (20, 20))
    if game_over:
        font = pygame.font.SysFont(None, 60)
        text = font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(text, (20, 250))
    pygame.display.flip()