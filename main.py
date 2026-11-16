import pygame
import random
import math
import os
import sys
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
planet_count=1
black_screen=pygame.Surface((1500,850),pygame.SRCALPHA)
darkness=255
for i in range(1000):
    stars.append((random.randint(0,1500),random.randint(0,850),random.randint(1,2),(random.randint(125,255),random.randint(125,255),random.randint(125,255))))

def draw_glow(radius,color):
    size=radius*2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r in range(radius,0, -1):
        falloff = (1-r/radius)**2
        alpha = int(255 * falloff)
        pygame.draw.circle(surf, (*color, alpha),(radius, radius), r)
    return surf
def get_glow(glow_cache,color,radius):
    radius=max(1,int(radius))
    if radius not in glow_cache:
        glow_cache[radius]=draw_glow(radius,color)
    return glow_cache[radius]
class ShootingStar:
    def __init__(self):
        self.pos=pygame.Vector2(200,random.randint(200,650))
        self.speed=100
        self.color=(0,40,80)
        self.radius=7
        self.velocity=pygame.Vector2(0,0)
        self.tail_steps=100
        self.glow_cache={}
        self.tail_end=self.pos
    def draw(self,screen):
        glow_surf=get_glow(self.glow_cache,self.color,self.radius*3)
        screen.blit(glow_surf, glow_surf.get_rect(center=self.pos),special_flags=pygame.BLEND_RGBA_ADD)
        self.pos+=self.velocity*0.25
        self.tail_end+=self.velocity*0.2
    def draw_tail(self,screen,start,end):
        for i in range(self.tail_steps):
            t=i/self.tail_steps
            pos=start+(end-start)*t
            radius=self.radius*(1-t)*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            rect = glow.get_rect(center=pos)
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
def shuffle():
    global stars, planets, planets_pos,completed
    stars=[]
    for i in range(random.randint(200,1200)):
        stars.append((random.randint(0,1500),random.randint(0,850),random.randint(1,2),(random.randint(125,255),random.randint(125,255),random.randint(125,255))))
    planets=[]
    planets_pos=set()
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
    player.pos=pygame.Vector2(200,random.randint(200,650))
    goal.pos=pygame.Vector2(1400,random.randint(200,650))
    player.velocity=pygame.Vector2(0,0)
    player.tail_end=player.pos
    completed=False
def reset():
    player.pos=pygame.Vector2(200,random.randint(200,650))
    player.velocity=pygame.Vector2(0,0)
    player.tail_end=player.pos
goal=Goal()
player=ShootingStar()
dragging=False
planets=[]
planets_pos=set()
level=1
lives=3
completed=False
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

running=True
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
                player.velocity=pygame.Vector2(0,0)
                player.tail_end=player.pos
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if player.pos.distance_to(event.pos)<player.radius*2:
                dragging=True
        elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
            dragging=False
            cursor=pygame.Vector2(pygame.mouse.get_pos())
            player.velocity=(player.pos-cursor)*0.1
                
    #Logic
    for planet in planets:
        if player.pos.distance_to(planet.pos)<(player.radius+planet.radius)*1.5:
            reset()
            lives-=1
            darkness=200
    if player.pos.x>1600 or player.pos.x<-100 or player.pos.y>950 or player.pos.y<-100:
        reset()
        lives-=1
        darkness=200
    if player.pos.distance_to(goal.pos)<(player.radius+goal.radius)*2 and not completed:
        level+=1
        completed=True
        if planet_count<3:
            planet_count+=1
        shuffle()
        darkness=255
    if lives<=0:
        running=False


    #Rendering
    screen.fill((8,8,24))
    for x,y,r,color in stars:
        pygame.draw.circle(screen,color,(x,y),r)
    for planet in planets:
        planet.draw(screen,planet.pos,planet.pos)
    player.draw(screen)
    player.draw_tail(screen,player.pos,player.tail_end)
    goal.draw(screen,goal.pos,goal.pos)
    if dragging:
        cursor=pygame.Vector2(pygame.mouse.get_pos())
        pygame.draw.circle(screen,(200,200,200),cursor,10)
        if cursor.distance_to(player.pos)>=0:
            player.tail_end=cursor

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