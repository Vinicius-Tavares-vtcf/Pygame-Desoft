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
MUSICA_MIDGAME = 'musica_midgame'
HOVER_SAIR = 'hover_sair'
ARENA_COLISEU = 'Arena_Coliseu'
ARENA_FOGO = 'Arena_Fogo'
ARENA_ALIEN = 'Arena_Alien'
VIDEO_TRANSICAO = 'video_transicao'
VIDEO_TRANSICAO_ALIEN = 'video_transicao_alien'
MEDKIT = 'medkit'

WEAPON_CABIN = 'weapon_cabin'
WEAPON_ESPADA = 'weapon_espada'
WEAPON_ARCO = 'weapon_arco'
WEAPON_CAJADO = 'weapon_cajado'
WEAPON_ESPADA_EVO = 'weapon_espada_evo'
WEAPON_ARCO_EVO = 'weapon_arco_evo'
WEAPON_CAJADO_EVO = 'weapon_cajado_evo'
ENEMY_ESQUELETO = 'esqueleto'
ENEMY_ESQUELETO_EVO = 'esqueleto_evo'
ENEMY_LOBISOMEM = 'lobisomem'
ENEMY_LOBISOMEM_EVO = 'lobisomem_evo'
ENEMY_LEAO = 'leao'
ENEMY_LEAO_EVO = 'leao_evo'
ENEMY_MAGO = 'mago'
ENEMY_MAGO_EVO = 'mago_evo'
ENEMY_MINOTAURO = 'minotauro'

SFX_SWORD = 'sfx_sword'
SFX_HIT = 'sfx_hit'
SFX_FIREBALL = 'sfx_fireball'
SFX_ENEMY_DEATH = 'sfx_enemy_death'
SFX_MONSTER_BITE = 'sfx_monster_bite'
SFX_MONSTER_DEATH = 'sfx_monster_death'
SFX_MAGE_DEATH = 'sfx_mage_death'
SFX_MINOTAUR_DEATH = 'sfx_minotaur_death'
SFX_MINOTAUR_ATTACK = 'sfx_minotaur_attack'


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

    background_fogo = pygame.image.load(path.join(IMG_DIR, 'Arena_Fogo.jpeg')).convert_alpha()
    assets[ARENA_FOGO] = pygame.transform.smoothscale(background_fogo, (int(LARGURA_TELA * 2.5), int(ALTURA_TELA * 2.5)))
    assets[VIDEO_TRANSICAO] = path.join(IMG_DIR, 'ColiseuPegandoFogo.mp4')

    background_alien = pygame.image.load(path.join(IMG_DIR, 'Arena_Alien.jpeg')).convert_alpha()
    assets[ARENA_ALIEN] = pygame.transform.smoothscale(background_alien, (int(LARGURA_TELA * 2.5), int(ALTURA_TELA * 2.5)))
    assets[VIDEO_TRANSICAO_ALIEN] = path.join(IMG_DIR, 'Arena_Alien_Video.mp4')

    assets['player_sheet'] = pygame.image.load(path.join(IMG_DIR, 'PersonagemRomano32bit.png')).convert_alpha()
    assets[ENEMY_ESQUELETO] = pygame.image.load(path.join(IMG_DIR, 'Esqueleto32bit.png')).convert_alpha()
    assets[ENEMY_ESQUELETO_EVO] = pygame.image.load(path.join(IMG_DIR, 'Esqueleto32bitV1.png')).convert_alpha()
    assets[ENEMY_LOBISOMEM] = pygame.image.load(path.join(IMG_DIR, 'Lobisomem32bit.png')).convert_alpha()
    assets[ENEMY_LOBISOMEM_EVO] = assets[ENEMY_LOBISOMEM]
    assets[ENEMY_LEAO] = pygame.image.load(path.join(IMG_DIR, 'Leão32bit.png')).convert_alpha()
    assets[ENEMY_LEAO_EVO] = pygame.image.load(path.join(IMG_DIR, 'Leão32bitV1.png')).convert_alpha()
    assets[ENEMY_MINOTAURO] = pygame.image.load(path.join(IMG_DIR, 'Minotauro32bit.png')).convert_alpha()

    assets[MEDKIT] = _load_scaled_image(IMG_DIR, 'Totemdecura32bit.png', (280, 280))
    assets[WEAPON_CABIN] = pygame.transform.smoothscale(
        pygame.image.load(path.join(IMG_DIR, 'Cabana_Armas32bit.png')).convert_alpha(),
        (450, 450)
    )
    assets['medkit_pickup'] = pygame.image.load(path.join(IMG_DIR, 'medkit.png')).convert_alpha()

    assets['arrow'] = pygame.transform.smoothscale(
    pygame.image.load(path.join(IMG_DIR, 'Flecha.png')).convert_alpha(),
    (48, 48)
)
    
    mage_sheet = pygame.image.load(path.join(IMG_DIR, 'Mago_Parado32bit.png')).convert_alpha()

    w = mage_sheet.get_width() // 2
    h = mage_sheet.get_height()

    left = mage_sheet.subsurface((0, 0, w, h)).copy()
    right = mage_sheet.subsurface((w, 0, w, h)).copy()

    # remove fundo/transparência sobrando
    left_rect = left.get_bounding_rect()
    right_rect = right.get_bounding_rect()

    if left_rect.width > 0 and left_rect.height > 0:
        left = left.subsurface(left_rect).copy()

    if right_rect.width > 0 and right_rect.height > 0:
        right = right.subsurface(right_rect).copy()

    # reduz tamanho
    scale = 0.35

    left = pygame.transform.smoothscale(
        left,
        (int(left.get_width() * scale), int(left.get_height() * scale))
    )

    right = pygame.transform.smoothscale(
        right,
        (int(right.get_width() * scale), int(right.get_height() * scale))
    )

    assets['mago_left'] = left
    assets['mago_right'] = right

    def _split_mage_sheet(filename, scale=0.35):
        sheet = pygame.image.load(path.join(IMG_DIR, filename)).convert_alpha()
        w = sheet.get_width() // 2
        h = sheet.get_height()
        l = sheet.subsurface((0, 0, w, h)).copy()
        r = sheet.subsurface((w, 0, w, h)).copy()
        lr = l.get_bounding_rect()
        rr = r.get_bounding_rect()
        if lr.width > 0 and lr.height > 0:
            l = l.subsurface(lr).copy()
        if rr.width > 0 and rr.height > 0:
            r = r.subsurface(rr).copy()
        l = pygame.transform.smoothscale(l, (int(l.get_width() * scale), int(l.get_height() * scale)))
        r = pygame.transform.smoothscale(r, (int(r.get_width() * scale), int(r.get_height() * scale)))
        return l, r

    mago_evo_left, mago_evo_right = _split_mage_sheet('Mago32bitV1.png')
    assets['mago_evo_left'] = mago_evo_left
    assets['mago_evo_right'] = mago_evo_right

    mago_space_left, mago_space_right = _split_mage_sheet('Mago32bitV2.png')
    assets['mago_space_left'] = mago_space_left
    assets['mago_space_right'] = mago_space_right

    assets['esqueleto_space_sheet'] = pygame.image.load(path.join(IMG_DIR, 'Esqueleto32bitV2.png')).convert_alpha()
    assets['lobisomem_space_sheet'] = pygame.image.load(path.join(IMG_DIR, 'Lobisomem32bitV2.png')).convert_alpha()
    assets['leao_space_sheet']      = pygame.image.load(path.join(IMG_DIR, 'Leão32bitV2.png')).convert_alpha()

    # As armas no mapa e na mao do personagem precisam ficar maiores para serem visiveis.
    assets[WEAPON_ESPADA] = pygame.image.load(path.join(IMG_DIR, 'Espada32bit.png')).convert_alpha()
    assets[WEAPON_ARCO] = pygame.image.load(path.join(IMG_DIR, 'Arco32bit.png')).convert_alpha()
    assets[WEAPON_CAJADO] = pygame.image.load(path.join(IMG_DIR, 'Cajado32bit.png')).convert_alpha()

    _espada_evo_sheet = pygame.image.load(path.join(IMG_DIR, 'Espada32bitV1.png')).convert_alpha()
    assets[WEAPON_ESPADA_EVO] = _espada_evo_sheet
    _fw = _espada_evo_sheet.get_width() // 8
    _fh = _espada_evo_sheet.get_height() // 8
    _raw = _espada_evo_sheet.subsurface((0 * _fw, 3 * _fh, _fw, _fh)).copy()
    assets['weapon_espada_evo_frame'] = pygame.transform.smoothscale(
        _raw, (int(_raw.get_width() * 0.45), int(_raw.get_height() * 0.45))
    )
    assets[WEAPON_CAJADO_EVO] = pygame.image.load(path.join(IMG_DIR, 'Cajado32bitV1.png')).convert_alpha()
    arco_evo = assets[WEAPON_ARCO].copy()
    arco_evo.fill((255, 100, 65), special_flags=pygame.BLEND_RGBA_MULT)
    assets[WEAPON_ARCO_EVO] = arco_evo

    assets['arrow_fire'] = pygame.transform.smoothscale(
        pygame.image.load(path.join(IMG_DIR, 'FlechaV1.png')).convert_alpha(),
        (48, 48)
    )

    _SPACE_TINT = (65, 120, 255)

    _espada_space = assets[WEAPON_ESPADA].copy()
    _espada_space.fill((255, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    _espada_space.fill((50, 0, 160), special_flags=pygame.BLEND_ADD)
    assets['weapon_espada_space'] = _espada_space

    _cajado_space = assets[WEAPON_CAJADO].copy()
    _cajado_space.fill((255, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)  # zera canal verde
    _cajado_space.fill((50, 0, 160), special_flags=pygame.BLEND_ADD)         # adiciona roxo/azul
    assets['weapon_cajado_space'] = _cajado_space

    _arco_space = assets[WEAPON_ARCO].copy()
    _arco_space.fill(_SPACE_TINT, special_flags=pygame.BLEND_RGBA_MULT)
    assets['weapon_arco_space'] = _arco_space

    assets['arrow_space'] = pygame.transform.smoothscale(
        pygame.image.load(path.join(IMG_DIR, 'FlechaV2.png')).convert_alpha(),
        (48, 48)
    )

    def load_spell(name):
        img = pygame.image.load(path.join(IMG_DIR, name)).convert_alpha()
        return pygame.transform.smoothscale(img, (180, 180))

    assets['water_spell_1'] = load_spell('Water__0132bit.png')
    assets['water_spell_2'] = load_spell('Water__0232bit.png')
    assets['water_spell_3'] = load_spell('Water__0332bit.png')
    assets['water_spell_4'] = load_spell('Water__0432bit.png')
    assets['water_spell_5'] = load_spell('Water__0532bit.png')

    assets['fire_spell_1'] = load_spell('Fire_0132bit.png')
    assets['fire_spell_2'] = load_spell('Fire_0232bit.png')
    assets['fire_spell_3'] = load_spell('Fire_0332bit.png')
    assets['fire_spell_4'] = load_spell('Fire_0432bit.png')
    assets['fire_spell_5'] = load_spell('Fire_0532bit.png')

    for i in range(1, 6):
        _s = assets[f'fire_spell_{i}'].copy()
        _s.fill((180, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        _s.fill((0, 0, 100), special_flags=pygame.BLEND_ADD)
        assets[f'space_spell_{i}'] = _s

    # ----- Sons
    music_path = path.join(SND_DIR, 'Musica-Epica.mp3')
    assets[MUSICA_INICIAL] = music_path

    music_path = path.join(SND_DIR, 'Musica-Midgame.mp3')
    assets[MUSICA_MIDGAME] = music_path

    # O arquivo veio com nome quebrado em algumas copias do zip; tentamos achar a variante correta.
    sound_path = _load_optional_sound(SND_DIR, 'Rudgio Le*.ogg')
    assets[VIDEO_INICIAL] = sound_path

    # ----- Efeitos sonoros de combate
    assets[SFX_SWORD] = pygame.mixer.Sound(path.join(SND_DIR, 'combat', 'sword_slash.wav.mp3'))
    assets[SFX_HIT] = pygame.mixer.Sound(path.join(SND_DIR, 'combat', 'hit.wav.mp3'))
    assets[SFX_MONSTER_BITE] = pygame.mixer.Sound(path.join(SND_DIR, 'combat', 'monsterbite.waw.mp3'))
    assets[SFX_MINOTAUR_ATTACK] = pygame.mixer.Sound(path.join(SND_DIR, 'combat', 'ataqueminotauro.waw.mp3'))
    assets[SFX_FIREBALL] = pygame.mixer.Sound(path.join(SND_DIR, 'magic', 'fireball.wav.mp3'))
    assets[SFX_ENEMY_DEATH] = pygame.mixer.Sound(path.join(SND_DIR, 'enemy', 'death.wav.mp3'))
    assets[SFX_MONSTER_DEATH] = pygame.mixer.Sound(path.join(SND_DIR, 'enemy', 'monsterdeath.waw.mp3'))
    assets[SFX_MAGE_DEATH] = pygame.mixer.Sound(path.join(SND_DIR, 'enemy', 'mortemago.waw.mp3'))
    assets[SFX_MINOTAUR_DEATH] = pygame.mixer.Sound(path.join(SND_DIR, 'enemy', 'morteminotauro.waw.mp3'))

    assets[SFX_SWORD].set_volume(0.4)
    assets[SFX_HIT].set_volume(0.5)
    assets[SFX_MONSTER_BITE].set_volume(0.6)
    assets[SFX_MINOTAUR_ATTACK].set_volume(0.6)
    assets[SFX_FIREBALL].set_volume(0.5)
    assets[SFX_ENEMY_DEATH].set_volume(0.6)
    assets[SFX_MONSTER_DEATH].set_volume(0.6)
    assets[SFX_MAGE_DEATH].set_volume(0.6)
    assets[SFX_MINOTAUR_DEATH].set_volume(0.6)

    return assets
