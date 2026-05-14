import pygame
import random
from config import *
from os import path
from assets_loader import *


def game_screen(screen, assets):

    clock = pygame.time.Clock()

    background_arena = assets[ARENA_COLISEU]

    map_width = background_arena.get_width()
    map_height = background_arena.get_height()

    running = True
    state = GAME

    #Câmera começa no centro
    vcamerax = (map_width - LARGURA) // 2
    vcameray = (map_height - ALTURA) // 2

    speed = 20

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = QUIT
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            vcamerax -= speed
        if keys[pygame.K_d]:
            vcamerax += speed
        if keys[pygame.K_w]:
            vcameray -= speed
        if keys[pygame.K_s]:
            vcameray += speed

        #Limitando Câmera, para não sair do mapa
        vcamerax = max(0, min(vcamerax, map_width - LARGURA))
        vcameray = max(0, min(vcameray, map_height - ALTURA))

        screen.fill((0, 0, 0))
        screen.blit(background_arena, (-vcamerax, -vcameray))

        pygame.display.flip()

    return state