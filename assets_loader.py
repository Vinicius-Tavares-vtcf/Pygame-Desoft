# ===== Assets =====
import pygame
from os import path
import glob
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

WEAPON_ESPADA = 'weapon_espada'
WEAPON_ARCO = 'weapon_arco'
WEAPON_CAJADO = 'weapon_cajado'
ENEMY_ESQUELETO = 'esqueleto'
ENEMY_LOBISOMEM = 'lobisomem'
ENEMY_MAGO = 'mago'


def _load_optional_sound(folder, pattern):
    matches = sorted(glob.glob(path.join(folder, pattern)))
    return matches[0] if matches else None


def _load_scaled_image(folder, filename, size):
    image = pygame.image.load(path.join(folder, filename)).convert_alpha()
    return pygame.transform.smoothscale(image, size)


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
    assets[HOVER_BATALHAR] = pygame.transform.smoothscale(hover_batalhar, (int(650 * 1.03), int(222 * 1.03)))

    hover_sair = txt_sair.copy()
    hover_sair.fill((200, 150, 150), special_flags=pygame.BLEND_RGBA_MULT)
    assets[HOVER_SAIR] = pygame.transform.smoothscale(hover_sair, (int(320 * 1.03), int(184 * 1.03)))

    background_arena = pygame.image.load(path.join(IMG_DIR, 'Arena Coliseu.jpeg')).convert_alpha()
    assets[ARENA_COLISEU] = pygame.transform.smoothscale(background_arena, (int(LARGURA_TELA * 2.5), int(ALTURA_TELA * 2.5)))

    assets['player_sheet'] = pygame.image.load(path.join(IMG_DIR, 'Personagem32bit.png')).convert_alpha()
    assets[ENEMY_ESQUELETO] = pygame.image.load(path.join(IMG_DIR, 'Esqueleto.png')).convert_alpha()
    assets[ENEMY_LOBISOMEM] = pygame.image.load(path.join(IMG_DIR, 'Lobisomem.png')).convert_alpha()
    assets[ENEMY_MAGO] = pygame.image.load(path.join(IMG_DIR, 'Mago.png')).convert_alpha()

    # As armas no mapa e na mao do personagem precisam ficar maiores para serem visiveis.
    assets[WEAPON_ESPADA] = _load_scaled_image(IMG_DIR, 'Espada.png', (140, 140))
    assets[WEAPON_ARCO] = _load_scaled_image(IMG_DIR, 'Arco.png', (140, 140))
    assets[WEAPON_CAJADO] = _load_scaled_image(IMG_DIR, 'Cajado.png', (140, 140))

    # ----- Sons
    music_path = path.join(SND_DIR, 'Musica-Epica.mp3')
    assets[MUSICA_INICIAL] = music_path

    # O arquivo veio com nome quebrado em algumas copias do zip; tentamos achar a variante correta.
    sound_path = _load_optional_sound(SND_DIR, 'Rudgio Le*.ogg')
    assets[VIDEO_INICIAL] = sound_path

    return assets
