# ===== Assets =====
import pygame
from os import path
from config import *

# ----- Chaves dos assets
VIDEO_INICIAL = 'video_inicial'
TXT_TITULO = 'txt_titulo'
TXT_BATALHAR = 'txt_batalhar'
HOVER_BATALHAR = 'hover_batalhar'
TXT_SAIR = 'txt_sair'
MUSICA_INICIAL = 'musica_inicial'

HOVER_SAIR = 'hover_sair'
ARENA_COLISEU = 'Arena_Coliseu'

def load_assets():
    assets = {}

    # ----- Imagens
    txt_titulo = pygame.image.load(path.join(IMG_DIR, 'O-Coliseu.png')).convert_alpha()
    assets[TXT_TITULO] = pygame.transform.smoothscale(txt_titulo, (1050, 351))

    txt_batalhar = pygame.image.load(path.join(IMG_DIR, 'Batalhar.png')).convert_alpha()
    assets[TXT_BATALHAR] = pygame.transform.smoothscale(txt_batalhar, (650, 222))

    txt_sair = pygame.image.load(path.join(IMG_DIR, 'Sair.png')).convert_alpha()
    assets[TXT_SAIR] = pygame.transform.smoothscale(txt_sair, (320, 184))

    hover_batalhar = txt_batalhar.copy()
    hover_batalhar.fill((200, 150, 150), special_flags=pygame.BLEND_RGBA_MULT)
    assets[HOVER_BATALHAR]  = pygame.transform.smoothscale(hover_batalhar,(650*1.03,222*1.03))

    hover_sair = txt_sair.copy()
    hover_sair.fill((200, 150, 150), special_flags=pygame.BLEND_RGBA_MULT)
    assets[HOVER_SAIR] = pygame.transform.smoothscale(hover_sair,(320*1.03,184*1.03))

    background_arena = pygame.image.load(path.join(IMG_DIR, 'Arena Coliseu.jpeg')).convert_alpha()
    assets[ARENA_COLISEU] = pygame.transform.smoothscale(background_arena, (LARGURA*2.5, ALTURA*2.5))

    player_sheet = pygame.image.load(path.join(IMG_DIR, 'Personagem.png')).convert_alpha()
    assets["player_sheet"] = player_sheet

    # ----- Sons

    return assets