import pygame
import random
import math
import os
import sys
pygame.init()
pygame.mixer.init()

def get_resource_path(relative_path):
    try:
        base_path=sys._MEIPASS
    except Exception:
        base_path=os.path.abspath(".")
    return os.path.join(base_path, relative_path)
screen = pygame.display.set_mode((1500, 850))
is_fullscreen=False
pygame.display.set_caption("Shooting Star")

#Starry background



running=True
while running:
    #Input
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

    #Rendering
    screen.fill((8,8,24))
    pygame.display.flip() 
pygame.quit()