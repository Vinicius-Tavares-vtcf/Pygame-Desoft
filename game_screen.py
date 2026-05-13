import pygame
import random
from config import *
from os import path
from assets_loader import *


def game_screen(screen,assets):

    clock = pygame.time.Clock()

    background_arena = assets[ARENA_COLISEU]
    rect_background_arena = background_arena.get_rect(center=(LARGURA // 2, ALTURA // 2))
    running = True
    state = GAME

    vcamerax = 0
    vcameray = 0 
    while  running:
        clock.tick(FPS)
        rect_background_arena = background_arena.get_rect(center = (LARGURA // 2 + vcamerax, ALTURA // 2 + vcameray))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                state = QUIT
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    vcamerax += 8
                if event.key == pygame.K_d:
                    vcamerax -= 8                
                if event.key == pygame.K_w:
                    vcameray += 8
                if event.key == pygame.K_s:
                    vcameray -= 8
                
        screen.blit(background_arena,rect_background_arena)
        pygame.display.flip()

    return state