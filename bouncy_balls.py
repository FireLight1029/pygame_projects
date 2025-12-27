import pygame
pygame.init()
import math, random

paused = True
class Particle:
    def __init__(self, pos, vel, r = 10, color = None):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.r = r
        if color is None:
            self.color = (
            random.randint(50,255),
            random.randint(50,255),
            random.randint(50,255)
            )
        else:
            self.color = color
    def update(self, dt):
        g= 90
        self.vy += g*dt
        self.x += self.vx * dt
        self.y += self.vy * dt
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.r)

def off_screen(p):
    dx = p.x - cx
    dy = p.y - cy
    dist = math.hypot(dx, dy)
    if dist > R*1.2:
        return True

def reflection(p):
    dx = p.x - cx
    dy = p.y - cy
    dist = math.hypot(dx, dy)
    if dist+ p.r > R:
        #normal vector
        nx, ny = dx/dist, dy/dist
        vdotn = p.vx*nx + p.vy*ny
        p.vx -= 2*vdotn*nx
        p.vy -= 2*vdotn*ny

        p.x = cx + nx*(R - p.r - 0.5)
        p.y = cy + ny*(R - p.r - 0.5)

def collision(a,b):
    dx = a.x - b.x; dy = a.y - b.y
    return dx*dx + dy*dy <= (a.r + b.r)**2

def update(p):
    vx = p.vx;vy = p.vy
    vel = math.hypot(vx,vy)
    nx, ny = vx/vel, vy/vel
    if vel < 3000:
        vel += initial_speed*0.0005
    p.r += 0.003

    p.vx = nx*vel
    p.vy = ny*vel

W = 600
screen = pygame.display.set_mode((W, W))
clock = pygame.time.Clock()
running = True

cx, cy = W//2, W//2
R = 280

s = 250   # px/sec
initial_speed = 300
init_vector = (initial_speed*math.cos(math.pi/12),initial_speed*math.sin(math.pi/12))
particles = [Particle((cx,cy), (150,60))]
predator = Particle((cx + 100, cy), init_vector, r=30, color = (225, 50, 50))

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                paused = not paused

    screen.fill((0,0,0))           # black background
    pygame.draw.circle(screen, (100,100,100), (cx,cy), R, width=7)   # outline
    for part in particles:
        part.draw(screen)
    predator.draw(screen)
    dt = clock.tick(60) / 1000.0    
    if paused:
        dt = 0
        font = pygame.font.SysFont(None, 60)
        text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, (20, 20))
    elif not paused:

        for part in particles:
            part.update(dt)
            reflection(part)
        predator.update(dt)
        reflection(predator)
        #now we feast
        eaten = []
        new_part = []
        """
        for _ in range(2):
            angle = random.random() * 2*math.pi
            newx = cx + random.randint(0,45)
            newy = cy + random.randint(0,45)
            new_part.append(Particle((newx, newy), (s*math.cos(angle), s*math.sin(angle))))
        """
        limit = 10000
        balliter = 0        
        for i, part in enumerate(particles):

            if collision(part, predator):
                if balliter < limit:
                    eaten.append(i)
                    for _ in range(2):
                        angle = random.random() * 2*math.pi
                        newx = cx + random.randint(-100,100)
                        newy = cy + random.randint(-100,100)
                        new_part.append(Particle((newx, newy), (s*math.cos(angle), s*math.sin(angle))))
                    update(predator)
                    balliter += 1
                    if predator.r > R:
                        paused = True
        for i, part in enumerate(particles):
            if off_screen(part):
                eaten.append(i)
        for i in sorted(eaten, reverse = True):
            del particles[i]
        if len(particles) < 1000:
            particles.extend(new_part)
        pygame.display.flip()
pygame.quit()
