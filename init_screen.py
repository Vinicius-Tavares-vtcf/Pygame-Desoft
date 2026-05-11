# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
import random
from config import *
from os import path
import cv2

def init_screen(screen):
    clock = pygame.time.Clock()

    background = pygame.image.load(path.join(IMG_DIR, "Roman_warrior_fighting_lion.jpeg")).convert()
    background = pygame.transform.scale(background,(LARGURA,ALTURA))
    background_rect = background.get_rect()

    running = True
    
    while running:
    
        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                state = QUIT
                running = False
            if event.type == pygame.QUIT:
                state = QUIT
                running = False

        screen.blit(background,background_rect)
        pygame.display.flip()


    
    return state



