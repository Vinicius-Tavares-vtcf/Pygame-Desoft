# ===== Inicialização =====
# ----- Importa e inicia pacotesas
import pygame
import random
from config import *
from os import path
from init_screen import *
from assets_loader import *
import ctypes
from game_screen import *
from game_over import *
ctypes.windll.user32.SetProcessDPIAware()
pygame.init()
pygame.mixer.init()
# ----- Gera tela principal
window = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('O Coliseu')

# ----- Carrega assets
assets = load_assets()

state = INIT
player_name = ''
while state != QUIT:
    if state == INIT:
        state, player_name = init_screen(window, assets, player_name)
    if state == GAME:
        state = game_screen(window, assets, player_name)
    if state == GAME_OVER:
        state = game_over(window, assets)

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados

    
