# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
import random
from config import *
from os import path
from init_screen import *
from assets_loader import *
import ctypes
from game_screen import * 
ctypes.windll.user32.SetProcessDPIAware()
pygame.init()
pygame.mixer.init()

# ----- Gera tela principal
window = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('O Coliseu')

# ----- Carrega assets
assets = load_assets()


state = INIT
while state != QUIT:
    if state == INIT:
        state = init_screen(window, assets)
    if state == GAME:
        state = game_screen(window,assets)
        #state = game_screen(window, assets)
#      else:
#      state = game_over(window)
#          state = QUIT

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados

