import pygame
pygame.init()
import math, random
import numpy as np
class Particle:
    def __init__(self, pos, vel, r = 10, color = None):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.r = r
        self.e = 1000
        self.speed = math.hypot(self.vx, self.vy)
        if color is None:
            self.color = (
            random.randint(50,255),
            random.randint(50,255),
            random.randint(50,255)
            )
        else:
            self.color = color
    def update(self, dt):
        #g= 90
        #self.vy += g*dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.e -= 10
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.r)

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
        p.y = cx + ny*(R - p.r - 0.5)

def collision(a,b):
    dx = a.x - b.x; dy = a.y - b.y
    return dx*dx + dy*dy <= (a.r + b.r)**2

def mutations(vel, r):
    vel_mod_1 = 1.0 + random.choice([-0.01, 0, 0.01])
    vel_mod_2 = 1.0 + random.choice([-0.01, 0, 0.01])
    r_mod_1 = 1.0 + random.choice([-0.001, 0, 0.001])
    r_mod_2 = 1.0 + random.choice([-0.001, 0, 0.001])

    vel1 = vel * vel_mod_1
    vel2 = vel * vel_mod_2
    r1 = r * r_mod_1
    r2 = r * r_mod_2

    return vel1, vel2, r1, r2

def offspring(p):
    dx,dy = p.x, p.y
    vx,vy = p.vx, p.vy
    vel = math.hypot(vx,vy)
    angle = random.random() * 2 * math.pi
    conangle = 2* math.pi - angle
    vel1, vel2, r1, r2 = mutations(vel, p.r)
    new_pred = [
        Particle((dx,dy), (vel1*math.cos(angle), vel1*math.sin(angle)), r=r1, color = (225, 50, 50)),
        Particle((dx,dy), (vel2*math.cos(conangle), vel2*math.sin(conangle)), r=r2, color = (225, 50, 50)),
    ]
    return new_pred
W = 600
screen = pygame.display.set_mode((W, W))
clock = pygame.time.Clock()
running = True

cx, cy = W//2, W//2
R = 280

s = 150   # px/sec
particles = [Particle((cx,cy), (150,60))]
predators = [Particle((cx + 100, cy), (150, 60), r=20, color = (225, 50, 50))]

import matplotlib.pyplot as plt
plt.ion()
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
line1, = ax1.plot([],[],label = "Average Speed")
line2, = ax2.plot([],[],label = "Averaage Size")
line3, = ax3.plot([],[],label = "Number of Prey")
line4, = ax4.plot([],[],label = "Number of Predators")
ax1.set_ylabel("Speed")
ax2.set_ylabel("Size")
avg_speed_history = []
avg_size_history = []
prey_num_history = []
pred_num_history = []

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))           # black background
    pygame.draw.circle(screen, (100,100,100), (cx,cy), R, width=7)   # outline
    for part in particles:
        part.draw(screen)
    for predator in predators:
        predator.draw(screen)
    dt = clock.get_time()/1000.0
    for part in particles:
        part.update(dt)
        reflection(part)
    for predator in predators:
        predator.update(dt)
        reflection(predator)
    
    new_part = []
    #prey spawning
    preynum = random.randint(3,10)
    for _ in range(preynum):
        angle = random.random() * 2*math.pi
        spawnr = round(R/math.sqrt(2))
        newx = cx + random.randint(-spawnr, spawnr)
        newy = cy + random.randint(-spawnr, spawnr)
        new_part.append(Particle((newx, newy), (s*math.cos(angle), s*math.sin(angle))))
    #now we feast
    eaten = []
    for i, part in enumerate(particles):
        for j, predator in enumerate(predators):
            if collision(part, predator):
                eaten.append(i)
                predator.e += 30
    for i in sorted(set(eaten), reverse = True):
        del particles[i]
    reproduce = []
    new_pred = []
    for i, predator in enumerate(predators):
        if predator.e > 2000:
            reproduce.append(i)
            new_pred = offspring(predator)
        if predator.e < 0:
            reproduce.append(i)
    for i in sorted(reproduce, reverse = True):
        del predators[i]
    particles.extend(new_part)
    predators.extend(new_pred)
    
    avg_speed = np.mean([p.speed for p in predators])
    avg_size = np.mean([p.r for p in predators])
    avg_speed_history.append(avg_speed)
    avg_size_history.append(avg_size)
    prey_num_history.append(len(particles))
    pred_num_history.append(len(predators))


    line1.set_data(range(len(avg_speed_history)), avg_speed_history)
    line2.set_data(range(len(avg_size_history)), avg_size_history)
    line3.set_data(range(len(prey_num_history)), prey_num_history)
    line4.set_data(range(len(pred_num_history)), pred_num_history)
    ax1.relim(); ax2.relim(); ax3.relim(); ax4.relim()
    ax1.autoscale_view(); ax2.autoscale_view()
    ax3.autoscale_view(); ax4.autoscale_view()
    plt.draw()
    plt.pause(0.001)
    
    pygame.display.flip()
    clock.tick(30)
pygame.quit()