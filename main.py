import pygame
import random
import math
import os
import sys
from collections import deque
pygame.init()
pygame.mixer.init()

font=pygame.font.SysFont('Arial', 50)
def draw_text(text,font,color,x,y):
    img=font.render(text, True, color)
    screen.blit(img, (x, y))
screen = pygame.display.set_mode((1500, 850))
is_fullscreen=False
pygame.display.set_caption("Shooting Star")
clock=pygame.time.Clock()
#Starry background
stars=[]
planet_count=0
GRAVITY=9.81
black_screen=pygame.Surface((1500,850),pygame.SRCALPHA)
darkness=255
def draw_glow(radius,color):
    size=radius*2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r in range(radius,0, -1):
        falloff = (1-r/radius)**2
        alpha = int(255 * falloff)
        pygame.draw.circle(surf, (*color, alpha),(radius, radius), r)
    return surf
def draw_glow_rings(radius,color):
    w, h = radius * 8, radius * 2               
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        k = r / radius                           
        c = tuple(int(ch * (1 - k) ** 2) for ch in color)   
        rect = pygame.Rect(0, 0, int(w * k), int(h * k))
        rect.center = (w // 2, h // 2)
        pygame.draw.ellipse(surf, (*c, 255), rect)
    return surf
def get_glow(glow_cache,color,radius):
    radius=max(1,int(radius))
    if radius not in glow_cache:
        glow_cache[radius]=draw_glow(radius,color)
    return glow_cache[radius]
def get_glow_rings(glow_cache,color,radius):
    radius=max(1,int(radius))
    if radius not in glow_cache:
        glow_cache[radius]=draw_glow_rings(radius,color)
    return glow_cache[radius]
class ShootingStar:
    def __init__(self):
        self.pos=pygame.Vector2(200,random.randint(200,650))
        self.speed=100
        self.color=(0,40,80)
        self.radius=7
        self.velocity=pygame.Vector2(0,0)
        self.trail_len=100
        self.tail_steps=100
        self.tail_end=self.pos
        self.trail=deque(maxlen=self.trail_len)
        self.glow_cache={}
        self.launched=False
    def draw(self,screen):
        glow_surf=get_glow(self.glow_cache,self.color,self.radius*3)
        screen.blit(glow_surf, glow_surf.get_rect(center=self.pos),special_flags=pygame.BLEND_RGBA_ADD)
        self.pos+=self.velocity*0.25
        if self.launched:
            self.velocity+=gravity_at(self.pos)
            self.trail.append(self.pos.copy())
            self.trail.popleft()
    def stop(self):
        self.velocity=pygame.Vector2(0,0)
        self.tail_end=self.pos
        self.launched=False
    def reset(self):
        self.pos=pygame.Vector2(200,random.randint(200,650))
        self.velocity=pygame.Vector2(0,0)
        self.tail_end=self.pos
        self.launched=False
        self.trail.clear()
    def draw_tail(self,screen,start,end):
        for i in range(self.tail_steps):
            t=i/self.tail_steps
            pos=start+(end-start)*t
            radius=self.radius*(1-t)*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            rect = glow.get_rect(center=pos)
            screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)
    def draw_trail(self,screen):
        points=list(self.trail)
        n=len(points)
        if n<2:
            return
        for idx in range(n-1):
            radius=self.radius*(idx/(n-1))*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            rect=glow.get_rect(center=points[idx])
            screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)
class Meteor:
    def __init__(self):
        self.pos=pygame.Vector2(random.randint(0,1500),0)
        self.speed=100
        self.color=(random.randint(10,80),random.randint(10,80),random.randint(10,80))
        self.radius=5
        self.velocity=pygame.Vector2(20,0).rotate(random.randint(10,170))
        self.trail_len=100
        self.tail_steps=100
        self.tail_end=self.pos
        self.trail=deque(maxlen=self.trail_len)
        self.glow_cache={}
    def draw(self,screen):
        glow_surf=get_glow(self.glow_cache,self.color,self.radius*3)
        screen.blit(glow_surf, glow_surf.get_rect(center=self.pos),special_flags=pygame.BLEND_RGBA_ADD)
        self.pos+=self.velocity*0.25
        self.velocity+=gravity_at(self.pos)
        self.trail.append(self.pos.copy())
    def draw_trail(self,screen):
        points=list(self.trail)
        n=len(points)
        if n<2:
            return
        for idx in range(n-1):
            radius=self.radius*(idx/(n-1))*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            rect=glow.get_rect(center=points[idx])
            screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)


class Planet:
    def __init__(self,pos):        
        self.pos=pos
        self.speed=100
        self.color=(random.randint(0,50),random.randint(0,50),random.randint(0,20))
        self.ring_color=(self.color[0]+150,self.color[1]+150,self.color[2]+150)
        self.radius=random.randint(20,50)
        self.tail_steps=15
        self.glow_cache={}
    def draw(self,screen,start,end):
            for i in range(self.tail_steps):
                t=i/self.tail_steps
                pos=start+(end-start)*t
                radius=self.radius*(1-t)*1.6+2
                glow=get_glow(self.glow_cache,self.color,radius*1.5)
                rect = glow.get_rect(center=pos)
                screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)
            for i in range(3):
                pygame.draw.circle(screen,self.ring_color,pos,self.radius*3+i*20,2)
class Goal:
    def __init__(self):        
            self.pos=pygame.Vector2(1400,random.randint(100,750))
            self.color=(0,80,40)
            self.radius=20
            self.tail_steps=15
            self.glow_cache={}
    def draw(self,screen,start,end):
        for i in range(self.tail_steps):
            t=i/self.tail_steps
            pos=start+(end-start)*t
            radius=self.radius*(1-t)*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            rect = glow.get_rect(center=pos)
            screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)
class BlackHole:
    def __init__(self):        
            self.pos=pygame.Vector2(500,random.randint(100,750))
            self.color=(80,70,10)
            self.radius=30
            self.tail_steps=15
            self.glow_cache={}
            self.ring_cache={}
    def draw(self,screen,start,end):
        for i in range(self.tail_steps):
            t=i/self.tail_steps
            pos=start+(end-start)*t
            radius=self.radius*(1-t)*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            ring=get_glow_rings(self.ring_cache,self.color,radius*1.5)
            rect = glow.get_rect(center=pos)
            ring_rect=ring.get_rect(center=pos)
            screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(ring, ring_rect, special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.circle(screen,(0,0,0),pos,self.radius*2)
class WhiteHole:
    def __init__(self):        
            self.pos=pygame.Vector2(500,random.randint(100,750))
            self.color=(10,70,80)
            self.radius=30
            self.tail_steps=15
            self.glow_cache={}
            self.ring_cache={}
    def draw(self,screen,start,end):
        for i in range(self.tail_steps):
            t=i/self.tail_steps
            pos=start+(end-start)*t
            radius=self.radius*(1-t)*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            ring=get_glow_rings(self.ring_cache,self.color,radius*1.5)
            rect = glow.get_rect(center=pos)
            ring_rect=ring.get_rect(center=pos)
            screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(ring, ring_rect, special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.circle(screen,(255,255,255),pos,self.radius*2)
def shuffle():
    valid_white=False
    global stars, planets, planets_pos,completed, meteors
    stars=[]
    for i in range(random.randint(200,1200)):
        stars.append((random.randint(0,1500),random.randint(0,850),random.randint(1,2),(random.randint(125,255),random.randint(125,255),random.randint(125,255))))
    planets=[]
    planets_pos=set()
    x,y=random.randint(400,1100),random.randint(100,750)
    planets_pos.add((x,y))
    blackhole.pos=pygame.Vector2(x,y)
    x,y=random.randint(600,1300),random.randint(100,750)
    while not valid_white:
        if math.hypot(x-blackhole.pos.x,y-blackhole.pos.y)<200:
            x,y=random.randint(400,1300),random.randint(100,750)
        else:
            valid_white=True
    whitehole.pos=pygame.Vector2(x,y)
    planets_pos.add((x,y))
    while len(planets)<planet_count:
        valid=True
        x=random.randint(400,1300)
        y=random.randint(100,750)
        for px,py in planets_pos:
            if math.hypot(x-px,y-py)<300:
                valid=False
        if valid:
            planets_pos.add((x,y))
            planets.append(Planet(pygame.Vector2(x,y)))
    goal.pos=pygame.Vector2(1400,random.randint(200,650))
    completed=False
    player.reset()
    meteors=[]
class Particle:
    def __init__(self,pos,velocity,color):
        self.pos=pygame.Vector2(pos.x,pos.y)
        self.velocity=pygame.Vector2(velocity.x,velocity.y)
        self.color=color
        self.radius=20
    def draw(self,screen):
        pygame.draw.circle(screen,self.color,self.pos,self.radius)
        self.pos+=self.velocity*0.2
        self.radius-=1
particles=[]
def reset():
    player.reset()
def gravity_at(p):
    a=pygame.Vector2(0,0)
    for planet in planets:
        d=planet.pos-p
        distance=max(d.length(),20)
        strength=GRAVITY*planet.radius**2/(distance**2)
        a+=d/distance*strength
    if level>4:
        black=blackhole.pos-p
        distance=max(black.length(),20)
        strength=GRAVITY*blackhole.radius**4/(distance**2)*0.002
        a+=black/distance*strength
        white=whitehole.pos-p
        distance=max(white.length(),20)
        strength=GRAVITY*whitehole.radius**2/(distance**2)*0.5
        a-=white/distance*strength
    return a
goal=Goal()
blackhole=BlackHole()
whitehole=WhiteHole()
player=ShootingStar()
dragging=False
planets=[]
planets_pos=set()
level=1
lives=3
completed=False
collision_timer=1.5
meteor_spawn_timer=5
collided=False
shuffle()
running=True
meteors=[]
while running:
    #Input
    dt=clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_f:
                is_fullscreen= not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((1500, 850), pygame.FULLSCREEN|pygame.SCALED)
                else:
                    screen = pygame.display.set_mode((1500, 850))
            if event.key==pygame.K_SPACE:
                player.stop()
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if player.pos.distance_to(event.pos)<player.radius*2:
                dragging=True
        elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
            if dragging:
                dragging=False
                cursor=pygame.Vector2(pygame.mouse.get_pos())
                player.velocity=(player.pos-cursor)*0.1
                for i in range(player.trail_len):
                    player.trail.append(cursor.lerp(player.pos,i/player.trail_len))
                player.launched=True

    #Logic
    if level>6:
        meteor_spawn_timer-=dt
    if meteor_spawn_timer<=0:
        meteor_spawn_timer=max(3,10-level/3)
        meteors.append(Meteor())
    for planet in planets:
        if player.pos.distance_to(planet.pos)<(player.radius+planet.radius)*1.5:
            collision_timer-=dt
            collided=True
            if collided:
                for i in range(15):
                    velocity=player.velocity.rotate(random.uniform(-360,360))
                    color=(planet.color[0]+200,planet.color[1]+200,planet.color[2]+200)
                    particles.append(Particle(player.pos,velocity,color))
                collided=False
            player.stop()
            if collision_timer<=0:
                reset()
                lives-=1
                darkness=200
                collision_timer=1.5
    if player.pos.x>1500 or player.pos.x<0 or player.pos.y>850 or player.pos.y<0:
        reset()
        lives-=1
        darkness=200
    if player.pos.distance_to(goal.pos)<(player.radius+goal.radius)*2 and not completed:
        level+=1
        lives=3
        completed=True
        if planet_count<3:
            planet_count+=1
        shuffle()
        darkness=255
    if lives<=0:
        level=1
        planet_count=1
        lives=3
        shuffle()
    if player.pos.distance_to(blackhole.pos)<(player.radius+blackhole.radius)*2 and level>4:
        player.pos.x,player.pos.y=whitehole.pos.x,whitehole.pos.y
    for meteor in meteors:
        if meteor.pos.distance_to(blackhole.pos)<(meteor.radius+blackhole.radius)*2:
            meteor.pos.x,meteor.pos.y=whitehole.pos.x,whitehole.pos.y
        for planet in planets:
            if meteor.pos.distance_to(planet.pos)<(meteor.radius+planet.radius)*2:
                for i in range(5):
                    velocity=meteor.velocity.rotate(random.uniform(-360,360))
                    color=(planet.color[0]+200,planet.color[1]+200,planet.color[2]+200)
                    particles.append(Particle(meteor.pos,velocity,color))
                meteors.remove(meteor)
        if meteor.pos.distance_to(player.pos)<(meteor.radius+player.radius)*2:
            reset()
            lives-=1
            darkness=200
            for i in range(5):
                velocity=meteor.velocity.rotate(random.uniform(-360,360))
                particles.append(Particle(meteor.pos,velocity,meteor.color))
            meteors.remove(meteor)
        if meteor.pos.x<-100 or meteor.pos.x>1600 or meteor.pos.y<-100 or meteor.pos.y>900:
            meteors.remove(meteor)


    #Rendering
    screen.fill((8,8,24))
    for x,y,r,color in stars:
        pygame.draw.circle(screen,color,(x,y),r)
    for planet in planets:
        planet.draw(screen,planet.pos,planet.pos)
    if level>4:
        blackhole.draw(screen,blackhole.pos,blackhole.pos)
        whitehole.draw(screen,whitehole.pos,whitehole.pos)
    player.draw(screen)
    player.draw_trail(screen)
    for meteor in meteors:
        meteor.draw(screen)
        meteor.draw_trail(screen)
    goal.draw(screen,goal.pos,goal.pos)
    if dragging:
        cursor=pygame.Vector2(pygame.mouse.get_pos())
        pygame.draw.circle(screen,(200,200,200),cursor,10)
        player.draw_tail(screen,player.pos,player.tail_end)
        if cursor.distance_to(player.pos)>=0:
            player.tail_end=cursor
    if not player.launched:
        player.draw_tail(screen,player.pos,player.tail_end)        
    for particle in particles:
        if particle.radius>0:
            particle.draw(screen)
        else:
            particles.remove(particle)
    black_screen.fill((0,0,0,darkness))
    screen.blit(black_screen,(0,0))
    if darkness>=0:
        darkness-=dt*50
        if darkness>150:
            draw_text(f'Level {level}',font,(255,255,255),300,350)
            draw_text(f'Lives: {lives}',font,(255,255,255),300,400)
            draw_text(f'Drag and release the blue shooting star to shoot',font,(255,255,255),550,100)
            draw_text(f'Press space to stop your star',font,(255,255,255),550,200)
            draw_text(f'Reach the green star without touching any planet',font,(255,255,255),550,300)
            draw_text(f'Press F to toggle fullscreen',font,(255,255,255),550,400)
    pygame.display.flip() 
pygame.quit()