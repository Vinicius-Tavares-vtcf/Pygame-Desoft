# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
import random

pygame.init()
pygame.mixer.init()

# ----- Gera tela principal
window = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption('Coliseu')

INIT = 0 
GAME = 1
QUIT = 2


state = INIT
# while state != QUIT:
#     if state == INIT:
#        # state = init_screen(window)
#     # elif state == GAME:
#     #     #state = game_screen(window)
#     # else:
#     #    # state = game_over(window)
#     #     state = QUIT

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados

