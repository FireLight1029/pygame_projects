import pygame
pygame.init()
import math, random

class snake:
    def __init__(self, pos, dir = [(0,1)], color = (225, 50, 50)):
        self.pos = pos
        self.head = pos[0]
        self.len = len(pos)
        self.x, self.y = pos[0]
        self.dir = dir
        self.color = color
    def update(self, power):
        snake_pos = self.pos
        head_x, head_y = snake_pos[0]
        
        if len(self.dir) > 1:
            del self.dir[0]
            dx, dy = self.dir[0]
        else:
            dx, dy = self.dir[0]
        new_head = (head_x+dx, head_y+dy)
        if head_x+dx > 14:
            new_head = (head_x+dx -15, head_y+dy)
        if head_x+dx < 0:
            new_head = (head_x+dx +15, head_y+dy)
        if head_y+dy > 14:
            new_head = (head_x+dx , head_y+dy -15)
        if head_y+dy < 0:
            new_head = (head_x+dx , head_y+dy +15)
        self.head = new_head
        if collide(self, power):
            self.eat()
            return Powerup(self)
        else:
            snake_pos.insert(0, new_head)
            snake_pos.pop()
            self.pos = snake_pos
            return power

    def eat(self):
        snake_pos = self.pos
        head_x, head_y = snake_pos[0]
        if len(self.dir) > 1:
            del self.dir[0]
            dx, dy = self.dir[0]
        else:
            dx, dy = self.dir[0]
        new_head = (head_x+dx, head_y+dy)
        snake_pos.insert(0, new_head)
        self.pos = snake_pos
        self.head = new_head
    def draw(self, surf):
        for i, sq in enumerate(self.pos):
            x, y = grid_to_pixel(sq)
            y += UI_BAR
            pygame.draw.rect(surf, (100,0,0), (x+1, y+1, 38,38), border_radius=10)
            if i == 0:
                pygame.draw.rect(surf, (255,80,80), (x+3, y+3, 34, 34), border_radius=8)
            else:
                pygame.draw.rect(surf, self.color, (x+4, y+4, 32, 32), border_radius=6)
class Powerup:
    def __init__(self, snake):
        while True:
            gridx = random.randint(0,14)
            gridy = random.randint(0,14)
            self.head = (gridx, gridy)
            if self.head not in snake.pos:
                self.x, self.y = grid_to_pixel((gridx, gridy))
                break
        self.color = (50, 200, 255)
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.x+4, self.y+4+UI_BAR, 32, 32), border_radius=10)

def collide(a, b):
    if a.head == b.head:
        return True
    else:
        return False

def grid_to_pixel(cell):
    r, c = cell
    return c * CELL, r * CELL

def suicide(snake):
    pos = snake.pos
    posset = set(pos)
    if len(posset) < len(pos):
        return True
GRID = 15
CELL = 40
UI_BAR = 80
W = GRID * CELL
H = W + UI_BAR
grid = [(r, c) for r in range(GRID) for c in range(GRID)]

screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
SNAKE_SPEED = 3
MOVE_DELAY = 1 / SNAKE_SPEED
timer = 0

running = True
paused = False
snake_ = snake([(7,7), (7,6), (7,5)])
power = Powerup(snake_)
score = 0
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                paused = not paused
            if ev.key == pygame.K_LEFT:
                dir_list = snake_.dir
                if len(dir_list) < 3:
                    if dir_list[0] != (0,1) and dir_list[0] != (0,-1):
                        dir_list.append((0,-1))
                        snake_.dir = dir_list
            if ev.key == pygame.K_RIGHT:
                dir_list = snake_.dir
                if len(dir_list) < 3:
                    if dir_list[0] != (0,-1) and dir_list[0] != (0,1):
                        dir_list.append((0,1))
                        snake_.dir = dir_list
            if ev.key == pygame.K_UP:
                dir_list = snake_.dir
                if len(dir_list) < 3:
                    if dir_list[0] != (1,0) and dir_list[0] != (-1,0):
                        dir_list.append((-1,0))
                        snake_.dir = dir_list
            if ev.key == pygame.K_DOWN:
                dir_list = snake_.dir
                if len(dir_list) < 3:
                    if dir_list[0] != (-1,0) and dir_list[0] != (1,0):
                        dir_list.append((1,0))
                        snake_.dir = dir_list
    dt = clock.tick(30) / 1000.0
    screen.fill((20,20,20))
    pygame.draw.rect(screen, (25,25,25), (0,0,W,UI_BAR))

    font = pygame.font.SysFont(None, 50)
    title = font.render("SNAKE GAME", True, (255, 255, 255))
    screen.blit(title, (20, 20))

    score_font = pygame.font.SysFont(None, 40)
    score_txt = score_font.render(f"Score: {len(snake_.pos)-3}", True, (200,200,200))
    screen.blit(score_txt, (W - 200, 25))

    
    for r in range(GRID):
        for c in range(GRID):
            x = c * CELL
            y = r * CELL + UI_BAR
            pygame.draw.rect(screen, (40, 40, 40), (x, y, CELL, CELL), width=1)
    if paused:
        font = pygame.font.SysFont(None, 60)
        text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, (W - 170, H - 80))
    else:
        timer += dt
        if timer > MOVE_DELAY:
            timer -= MOVE_DELAY
            power = snake_.update(power)

    power.draw(screen)
    snake_.draw(screen)
    if suicide(snake_):
        overlay = pygame.Surface((W,H))
        overlay.fill((0,0,0))
        overlay.set_alpha(150)
        screen.blit(overlay, (0,0))

        font = pygame.font.SysFont(None, 100)
        text = font.render("GAME OVER", True, (255,50,50))
        screen.blit(text, (50, W//2 - 50))
        pygame.display.flip()
        pygame.time.wait(2000)
    pygame.display.flip()