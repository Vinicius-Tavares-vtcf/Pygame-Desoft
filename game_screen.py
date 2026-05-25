import random
import pygame
import cv2
from os import path
from config import *
from assets_loader import *
from sprites import *
from ranking import save_score, sorted_ranking

spells = []
arrows = []
def _draw_text(screen, font, text, x, y, color=(255, 255, 255)):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


def _show_defeat_screen(screen):
    clock = pygame.time.Clock()
    background = screen.copy()
    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    defeat_font = pygame.font.Font(path.join(FONT_DIR, 'HyliaSerifBeta-Regular.otf'), 96)
    option_font = pygame.font.Font(path.join(FONT_DIR, 'HyliaSerifBeta-Regular.otf'), 54)
    text = defeat_font.render('Você perdeu', True, (255, 235, 220))
    text_rect = text.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2))
    options_start_ms = pygame.time.get_ticks() + 5_000

    running = True
    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        show_options = now >= options_start_ms
        mouse_pos = pygame.mouse.get_pos()

        play_again_color = (255, 235, 220)
        quit_color = (255, 235, 220)
        play_again_text = option_font.render('Jogar novamente', True, play_again_color)
        quit_text = option_font.render('Sair', True, quit_color)
        play_again_rect = play_again_text.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 115))
        quit_rect = quit_text.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 195))

        is_hover_play = show_options and play_again_rect.collidepoint(mouse_pos)
        is_hover_quit = show_options and quit_rect.collidepoint(mouse_pos)

        if show_options and (is_hover_play or is_hover_quit):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return QUIT
            if show_options and event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return INIT
                if quit_rect.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return QUIT

        alpha = 135 + int(25 * abs(pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.08).y))
        overlay.fill((160, 0, 0, alpha))
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(text, text_rect)
        if show_options:
            if is_hover_play:
                play_again_text = option_font.render('Jogar novamente', True, (255, 190, 170))
                play_again_text = pygame.transform.smoothscale(
                    play_again_text,
                    (int(play_again_text.get_width() * 1.03), int(play_again_text.get_height() * 1.03))
                )
                play_again_rect = play_again_text.get_rect(center=play_again_rect.center)
            if is_hover_quit:
                quit_text = option_font.render('Sair', True, (255, 190, 170))
                quit_text = pygame.transform.smoothscale(
                    quit_text,
                    (int(quit_text.get_width() * 1.03), int(quit_text.get_height() * 1.03))
                )
                quit_rect = quit_text.get_rect(center=quit_rect.center)
            screen.blit(play_again_text, play_again_rect)
            screen.blit(quit_text, quit_rect)
        pygame.display.flip()

    return QUIT


def _shrink_rect(rect, scale_x, scale_y):
    new_width = max(1, int(rect.width * scale_x))
    new_height = max(1, int(rect.height * scale_y))
    return pygame.Rect(0, 0, new_width, new_height).move(
        rect.centerx - new_width // 2,
        rect.centery - new_height // 2,
    )


def _player_collision_rect(player):
    return pygame.Rect(int(player.x) - 18, int(player.y) - 34, 36, 68)


def _tint_sprite_pixels(frame, tint_color):
    tinted = frame.copy()
    background_colors = {
        tinted.get_at((0, 0))[:3],
        tinted.get_at((tinted.get_width() - 1, 0))[:3],
        tinted.get_at((0, tinted.get_height() - 1))[:3],
        tinted.get_at((tinted.get_width() - 1, tinted.get_height() - 1))[:3],
    }

    tinted.lock()
    for x in range(tinted.get_width()):
        for y in range(tinted.get_height()):
            pixel = tinted.get_at((x, y))
            if pixel.a == 0 or pixel[:3] in background_colors:
                continue
            tinted.set_at((
                x,
                y
            ), (
                pixel.r * tint_color[0] // 255,
                pixel.g * tint_color[1] // 255,
                pixel.b * tint_color[2] // 255,
                pixel.a,
            ))
    tinted.unlock()

    return tinted


def _enemy_collision_rect(enemy):
    if isinstance(enemy, Minotauro):
        return _shrink_rect(enemy.rect(), 0.58, 0.60)
    return _shrink_rect(enemy.rect(), 0.45, 0.45)


def _enemy_damage_rect(enemy):
    if isinstance(enemy, Minotauro):
        return _shrink_rect(enemy.rect(), 1.74, 1.80)
    return _shrink_rect(enemy.rect(), 0.45, 0.45)


def _separate_characters(first, second, first_rect, second_rect, move_first=True, move_second=True):
    if not first_rect.colliderect(second_rect):
        return

    overlap_x = min(first_rect.right - second_rect.left, second_rect.right - first_rect.left)
    overlap_y = min(first_rect.bottom - second_rect.top, second_rect.bottom - first_rect.top)
    first_share = 0.5 if move_first and move_second else 1 if move_first else 0
    second_share = 0.5 if move_first and move_second else 1 if move_second else 0

    if overlap_x < overlap_y:
        direction = -1 if first_rect.centerx <= second_rect.centerx else 1
        push = (overlap_x + 1) * direction
        first.x += push * first_share
        second.x -= push * second_share
    else:
        direction = -1 if first_rect.centery <= second_rect.centery else 1
        push = (overlap_y + 1) * direction
        first.y += push * first_share
        second.y -= push * second_share


EVO_SPAWN_START_MS = 90_000  # 1:30
PHASE_1_MS = 15_000           # 0-15s:  só esqueleto
PHASE_2_MS = 30_000           # 15-30s: esqueleto + lobisomem
PHASE_3_MS = 45_000           # 30-45s: + mago
# 45s-1:30:                             + leao (pool completo)

def _choose_enemy_type(enemy_types, weights, allow_mago=True):
    if allow_mago:
        return random.choices(enemy_types, weights=weights, k=1)[0]

    filtered = [
        (enemy_type, weight)
        for enemy_type, weight in zip(enemy_types, weights)
        if 'mago' not in enemy_type
    ]
    filtered_types, filtered_weights = zip(*filtered)
    return random.choices(filtered_types, weights=filtered_weights, k=1)[0]


def _spawn_enemy(map_width, map_height, assets, elapsed_ms=0, post_boss=False, allow_mago=True):
    if post_boss:
        enemy_type = _choose_enemy_type(
            ['esqueleto_space', 'lobisomem_space', 'leao_space', 'mago_space'],
            [35, 28, 20, 17],
            allow_mago,
        )
    elif elapsed_ms >= EVO_SPAWN_START_MS:
        enemy_type = _choose_enemy_type(
            ['lobisomem_evo', 'mago_evo', 'esqueleto_evo', 'leao_evo'],
            [30, 22, 38, 10],
            allow_mago,
        )
    elif elapsed_ms >= PHASE_3_MS:
        enemy_type = _choose_enemy_type(
            ['esqueleto', 'lobisomem', 'mago', 'leao'],
            [45, 30, 20, 5],
            allow_mago,
        )
    elif elapsed_ms >= PHASE_2_MS:
        enemy_type = _choose_enemy_type(
            ['esqueleto', 'lobisomem', 'mago'],
            [50, 35, 15],
            allow_mago,
        )
    elif elapsed_ms >= PHASE_1_MS:
        enemy_type = random.choices(
            ['esqueleto', 'lobisomem'],
            weights=[60, 40],
            k=1
        )[0]
    else:
        enemy_type = 'esqueleto'

    if enemy_type in ('mago', 'mago_evo', 'mago_space'):
        centro_x = map_width // 2
        centro_y = map_height // 2
        raio = 760

        lado = random.choice(['left', 'right', 'up', 'down'])

        if lado == 'left':
            x = centro_x - raio - 50
            y = random.randint(centro_y - 250, centro_y + 250)
            side = 'left'
        elif lado == 'right':
            x = centro_x + raio + 50
            y = random.randint(centro_y - 250, centro_y + 250)
            side = 'right'
        elif lado == 'up':
            x = random.randint(centro_x - 250, centro_x + 250)
            y = centro_y - raio + 100
            side = 'left'
        else:
            x = random.randint(centro_x - 250, centro_x + 250)
            y = centro_y + raio
            side = 'right'

        if enemy_type == 'mago_space':
            return MagoSpace(x, y, assets, side=side)
        if enemy_type == 'mago_evo':
            return MagoEvo(x, y, assets, side=side)
        return Mago(x, y, assets, side=side)

    angle = random.uniform(0, 6.28318)
    arena_cx = map_width // 2
    arena_cy = map_height // 2
    perimeter_radius = 720
    vec = pygame.math.Vector2(1, 0).rotate_rad(angle)
    x = arena_cx + int(perimeter_radius * vec.x)
    y = arena_cy + int(perimeter_radius * vec.y)
    x = max(100, min(x, map_width - 100))
    y = max(100, min(y, map_height - 100))

    if enemy_type == 'esqueleto':
        return Esqueleto(x, y, assets)
    elif enemy_type == 'esqueleto_evo':
        return EsqueletoEvo(x, y, assets)
    elif enemy_type == 'esqueleto_space':
        return EsqueletoSpace(x, y, assets)
    elif enemy_type == 'leao':
        return Leao(x, y, assets)
    elif enemy_type == 'leao_evo':
        return LeaoEvo(x, y, assets)
    elif enemy_type == 'leao_space':
        return LeaoSpace(x, y, assets)
    elif enemy_type == 'lobisomem_evo':
        return LobisomemEvo(x, y, assets)
    elif enemy_type == 'lobisomem_space':
        return LobisomemSpace(x, y, assets)
    else:
        return Lobisomem(x, y, assets)


def _spawn_boss(map_width, map_height, assets):
    angle = random.uniform(0, 6.28318)
    distance = random.randint(360, 520)
    x = map_width // 2 + int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
    y = map_height // 2 + int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
    x = max(120, min(x, map_width - 120))
    y = max(120, min(y, map_height - 120))
    return Minotauro(x, y, assets)


def posiciona_arma(player, player_center_x, player_center_y, weapon_img):
    # Cada entrada: (offset_x, offset_y, rotacao)
    config = {
        'Espada': {
            'parado': {
                'right':      ( 15,   13,   -30), 'left':      ( 2, -32,  90), 'up':      ( 40, -15,  45), 'down':      (-20,  12, -90),
                'up_right':   ( 38,   5,   0), 'up_left':   ( 18 , -18,  90), 'down_right': ( -18, 17 , -90), 'down_left': (-24,  -4,  180),
            },
            'atacando': {
                'right':      ( 38, 6,   -30), 'left':      (-30, -10, 120), 'up':      (  0, -50,  45), 'down':      ( -2,  45, -90),
                'up_right':   ( 47, -35,   0), 'up_left':   (-25, -10, 90), 'down_right': ( 38,  34, -85), 'down_left': (-42,  25,  180),
            },
        },
        'Arco': {
            'parado': {
                'right':      (  18,  -8, 110), 'left':      (-26,  -3, -70), 'up':      (  2, -25, 270), 'down':      (  0,   5, -20),
                'up_right':   (  17,  -15, 110), 'up_left':   (-12,  -7, -70), 'down_right': (  14,  7,  45), 'down_left': ( -10,  3, -45),
            },
            'atacando': {
                'right':      ( 27, -28, 130), 'left':      (-26, -27, -70), 'up':      (  2, -25, 240), 'down':      (  7,  15,  10),
                'up_right':   ( 26, -32, 130), 'up_left':   (-20, -27, -70), 'down_right': ( 15,  -6,  90), 'down_left': ( -16,  0, -30),
            },
        },
        'Cajado': {
            'parado': {
                'right':      ( 25,   2,  65), 'left':      ( 5,  -1, 225), 'up':      ( 40,  12, 135), 'down':      (-20,  12,   0),
                'up_right':   ( 25,   6,  90), 'up_left':   ( 36,   2, 180), 'down_right': (  3,   9,  45), 'down_left': (  -25,   2,  -90),
            },
            'atacando': {
                'right':      ( 60, 0,  50), 'left':      (-40, -10, 230), 'up':      (  0, -57, 140), 'down':      ( -5,  45, -30),
                'up_right':   ( 52, -20,  90), 'up_left':   (-15, -14, 180), 'down_right': ( 28,  13,  15), 'down_left': (-28,  21,  -90),
            },
        },
        'Punhos': {
            'parado': {
                'right':      ( 34,   8,   0), 'left':      ( 40,   8, 180), 'up':      (  5, -36,  90), 'down':      (-25,  12, -90),
                'up_right':   ( 34,   8,   0), 'up_left':   ( 40,   8, 180), 'down_right': (  5,  10, -45), 'down_left': (  8,  10,  45),
            },
            'atacando': {
                'right':      ( 34,   8,   0), 'left':      ( 40,   8, 180), 'up':      (  5, -36,  90), 'down':      (-25,  12, -90),
                'up_right':   ( 20, -14,  45), 'up_left':   ( 40,   8, 180), 'down_right': (  5,  10, -45), 'down_left': (  8,  10,  45),
            },
        },
    }

    estado = 'atacando' if player.attacking else 'parado'
    dx, dy, angulo = config[player.weapon][estado][player.direction]

    if angulo != 0:
        weapon_img = pygame.transform.rotate(weapon_img, angulo)

    weapon_rect = weapon_img.get_rect()
    weapon_rect.center = (player_center_x + dx, player_center_y + dy)

    return weapon_img, weapon_rect



def game_screen(screen, assets, player_name='Jogador'):
    pygame.mixer.music.load(assets[MUSICA_MIDGAME])
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    background_arena = assets[ARENA_COLISEU]
    background_fogo = assets[ARENA_FOGO]
    map_width = background_arena.get_width()
    map_height = background_arena.get_height()

    background_alien = assets[ARENA_ALIEN]

    current_background = background_arena
    transition_cap = None
    transition_done = False
    transition_cap_alien = None
    transition_done_alien = False

    player = Player(map_width, map_height, assets)

    font_small = pygame.font.SysFont('arial', 24, bold=True)
    font_mid = pygame.font.SysFont('arial', 32, bold=True)

    # Cabana de armas
    CABIN_X = map_width // 2 + 640
    CABIN_Y = map_height // 2 - 530
    cabin_image = assets[WEAPON_CABIN]
    cabin_rect = cabin_image.get_rect(center=(CABIN_X, CABIN_Y))
    cabin_interact_rect = pygame.Rect(0, 0, 160, 160)
    cabin_interact_rect.center = (CABIN_X, CABIN_Y)

    DEBUG_FREE_SHOP = False # remover após testes
    WEAPON_BUY_PRICES  = {'Arco': 0, 'Cajado': 0, 'Espada': 0} if DEBUG_FREE_SHOP else {'Arco': 20, 'Cajado': 30, 'Espada': 40}
    WEAPON_UPGRADE_PRICE = 0 if DEBUG_FREE_SHOP else 50
    WEAPON_BASE_DAMAGE   = {'Espada': 4, 'Arco': 2, 'Cajado': 3, 'Punhos': 1}
    WEAPON_BASE_RANGE = {'Espada': 66, 'Cajado': 80}
    WEAPON_SHEETS     = {'Espada': assets[WEAPON_ESPADA], 'Arco': assets[WEAPON_ARCO], 'Cajado': assets[WEAPON_CAJADO]}
    WEAPON_EVO_SHEETS = {'Espada': assets[WEAPON_ESPADA_EVO], 'Arco': assets[WEAPON_ARCO_EVO], 'Cajado': assets[WEAPON_CAJADO_EVO]}
    owned_weapons   = {'Punhos'}
    weapon_upgrades = {'Arco': 0, 'Cajado': 0, 'Espada': 0}
    shop_open = False

    def bow_ready_on_right_click():
        return 'Arco' in owned_weapons and player.weapon in ('Espada', 'Cajado')

    def upgraded_weapon_damage(weapon_name):
        level = min(weapon_upgrades.get(weapon_name, 0), 2)
        multipliers = (1, 3, 5)
        return WEAPON_BASE_DAMAGE[weapon_name] * multipliers[level]

    def upgraded_weapon_range(weapon_name):
        level = min(weapon_upgrades.get(weapon_name, 0), 2)
        if weapon_name == 'Espada':
            multipliers = (1, 1.5, 4)
            return int(WEAPON_BASE_RANGE[weapon_name] * multipliers[level])

        multipliers = (1, 1.5, 2)
        return int(WEAPON_BASE_RANGE[weapon_name] * multipliers[level])

    def bow_damage():
        return upgraded_weapon_damage('Arco')

    def shoot_arrow(mouse_pos):
        center_screen = (LARGURA_TELA // 2, ALTURA_TELA // 2)
        target_x = player.x + (mouse_pos[0] - center_screen[0])
        target_y = player.y + (mouse_pos[1] - center_screen[1])

        arco_lvl = weapon_upgrades.get('Arco', 0)
        arrow_img = (assets['arrow_space'] if arco_lvl >= 2
                     else assets['arrow_fire'] if arco_lvl == 1
                     else assets['arrow'])
        arrows.append(
            Arrow(
                player.x,
                player.y,
                target_x,
                target_y,
                arrow_img,
                speed=18,
                damage=bow_damage()
            )
        )

    def apply_upgrade(weapon_name):
        level = weapon_upgrades.get(weapon_name, 0)
        if level >= 2:
            if weapon_name == 'Espada':
                player.equip(weapon_name, assets['weapon_espada_space'])
            elif weapon_name == 'Cajado':
                player.equip(weapon_name, assets['weapon_cajado_space'])
                if player.weapon_image:
                    img = player.weapon_image
                    player.weapon_image = pygame.transform.smoothscale(
                        img, (int(img.get_width() * 0.9), int(img.get_height() * 0.9))
                    )
            else:
                player.equip(weapon_name, assets['weapon_arco_space'])
        elif level == 1:
            if weapon_name == 'Espada':
                player.equip(weapon_name, weapon_frame=assets['weapon_espada_evo_frame'])
            else:
                player.equip(weapon_name, WEAPON_EVO_SHEETS[weapon_name])
            if weapon_name == 'Cajado' and player.weapon_image:
                img = player.weapon_image
                player.weapon_image = pygame.transform.smoothscale(
                    img, (int(img.get_width() * 0.9), int(img.get_height() * 0.9))
                )
        else:
            player.equip(weapon_name, WEAPON_SHEETS[weapon_name])
        player.weapon_damage = upgraded_weapon_damage(weapon_name)
        if weapon_name in WEAPON_BASE_RANGE:
            player.attack_range = upgraded_weapon_range(weapon_name)

    def equip_shop_weapon(weapon_name):
        if weapon_name == 'Arco' and any(w in owned_weapons for w in ('Espada', 'Cajado')):
            return 'Arco pronto no botao direito!'

        apply_upgrade(weapon_name)
        return f'{weapon_name} equipada!'

    BASE_WAVE_SIZE = 6
    MAX_WAVE_SIZE = 20
    WAVE_FIRST_GROWTH_MS = 45_000
    WAVE_GROWTH_INTERVAL_MS = 20_000
    WAVE_GROWTH_AMOUNT = 2
    MAX_SPAWN_BATCH = 3
    SPAWN_INTERVAL_MS = 1_500
    FAST_SPAWN_START_MS = 150_000
    FAST_SPAWN_INTERVAL_MS = 500
    BOSS_SPAWN_DELAY_AFTER_MAX_WAVE_MS = 15_000
    SPECIAL_UPGRADE_UNLOCK_MS = 70_000
    MAX_UPGRADE_UNLOCK_BEFORE_BOSS_MS = 20_000
    POST_BOSS_RESUME_DELAY_MS = 10_000
    POST_BOSS_BASE_WAVE_SIZE = 20
    POST_BOSS_GROWTH_INTERVAL_MS = 10_000
    MAX_MAGOS_NA_ARENA = 8
    max_wave_reached_ms = (
        WAVE_FIRST_GROWTH_MS
        + ((MAX_WAVE_SIZE - BASE_WAVE_SIZE) // WAVE_GROWTH_AMOUNT - 1) * WAVE_GROWTH_INTERVAL_MS
    )
    boss_spawn_elapsed_ms = max_wave_reached_ms + BOSS_SPAWN_DELAY_AFTER_MAX_WAVE_MS
    max_upgrade_unlock_ms = max(0, boss_spawn_elapsed_ms - MAX_UPGRADE_UNLOCK_BEFORE_BOSS_MS)
    MEDKIT_SPAWN_INTERVAL_MS = 20_000  # novo medkit a cada 20s
    MEDKIT_MAX = 3                      # máximo simultâneo
    MEDKIT_HEAL = 40

    game_start_ms = pygame.time.get_ticks()
    next_spawn_ms = game_start_ms + SPAWN_INTERVAL_MS
    next_medkit_ms = game_start_ms + MEDKIT_SPAWN_INTERVAL_MS
    medkit_spawns = []
    medkit_img = pygame.transform.smoothscale(assets['medkit_pickup'], (72, 72))
    boss_spawned = False
    boss_defeated_ms = None

    initial_enemy_count = min(MAX_SPAWN_BATCH, BASE_WAVE_SIZE)
    enemies = []
    for _ in range(initial_enemy_count):
        enemies.append(_spawn_enemy(
            map_width,
            map_height,
            assets,
            allow_mago=sum(1 for enemy in enemies if enemy.kind == 'mago') < MAX_MAGOS_NA_ARENA,
        ))
    spells = []

    running = True
    state = GAME
    vcamerax = (map_width - LARGURA_TELA) // 2
    vcameray = (map_height - ALTURA_TELA) // 2
    message = ''
    message_timer = 0
    shop_message = ''
    shop_message_timer = 0
    contact_damage_cooldowns = {}
    attack_hit_enemies = set()
    CONTACT_DAMAGE_COOLDOWN_MS = 300
    LOBISOMEM_DAMAGE_COOLDOWN_MS = 1500
    MINOTAURO_DAMAGE_COOLDOWN_MS = 3000

    WAVE_FREEZE_START_MS = 90_000   # 1:30 - congela wave
    WAVE_FREEZE_END_MS   = 210_000  # 3:30 - retoma crescimento

    def current_wave_size(now):
        if boss_defeated_ms is not None:
            resume_ms = boss_defeated_ms + POST_BOSS_RESUME_DELAY_MS
            if now < resume_ms:
                return 0

            growth_steps = (now - resume_ms) // POST_BOSS_GROWTH_INTERVAL_MS
            return POST_BOSS_BASE_WAVE_SIZE + growth_steps * WAVE_GROWTH_AMOUNT

        elapsed = now - game_start_ms
        if elapsed < WAVE_FIRST_GROWTH_MS:
            return BASE_WAVE_SIZE

        if WAVE_FREEZE_START_MS <= elapsed < WAVE_FREEZE_END_MS:
            elapsed = WAVE_FREEZE_START_MS

        growth_steps = 1 + (elapsed - WAVE_FIRST_GROWTH_MS) // WAVE_GROWTH_INTERVAL_MS
        return min(MAX_WAVE_SIZE, BASE_WAVE_SIZE + growth_steps * WAVE_GROWTH_AMOUNT)

    def current_spawn_interval(now):
        if now - game_start_ms >= FAST_SPAWN_START_MS:
            return FAST_SPAWN_INTERVAL_MS
        return SPAWN_INTERVAL_MS

    def current_medkit_spawn_interval():
        if boss_defeated_ms is not None:
            return MEDKIT_SPAWN_INTERVAL_MS // 3
        if transition_done:
            return MEDKIT_SPAWN_INTERVAL_MS // 2
        return MEDKIT_SPAWN_INTERVAL_MS

    def current_medkit_heal():
        if boss_defeated_ms is not None:
            return 100
        return MEDKIT_HEAL

    def current_elapsed_ms():
        return pygame.time.get_ticks() - game_start_ms

    def upgrade_unlocked(next_level):
        if next_level == 1:
            return current_elapsed_ms() >= SPECIAL_UPGRADE_UNLOCK_MS
        if next_level == 2:
            return current_elapsed_ms() >= max_upgrade_unlock_ms
        return True

    def upgrade_lock_message(next_level):
        if next_level == 1:
            return 'Armas especiais liberadas em 1min10s!'
        if next_level == 2:
            return 'Armas max liberadas 20s antes do Minotauro!'
        return ''

    def normal_enemy_count():
        return sum(1 for enemy in enemies if not isinstance(enemy, Minotauro))

    def mago_count():
        return sum(1 for enemy in enemies if enemy.kind in ('mago', ENEMY_MAGO_EVO, 'mago_space'))

    def boss_alive():
        return any(isinstance(enemy, Minotauro) for enemy in enemies)

    def maintain_enemy_count():
        nonlocal next_spawn_ms, boss_spawned

        now = pygame.time.get_ticks()
        boss_spawn_ms = game_start_ms + max_wave_reached_ms + BOSS_SPAWN_DELAY_AFTER_MAX_WAVE_MS
        if not boss_spawned and now >= boss_spawn_ms:
            enemies.clear()
            spells.clear()
            arrows.clear()
            contact_damage_cooldowns.clear()
            attack_hit_enemies.clear()
            enemies.append(_spawn_boss(map_width, map_height, assets))
            _play_sound(assets[SFX_MINOTAUR_ENTRY], repeats=5)
            boss_spawned = True
            return

        if boss_alive():
            return

        target_enemies = current_wave_size(now)
        missing_enemies = target_enemies - normal_enemy_count()
        if missing_enemies <= 0 or now < next_spawn_ms:
            return

        spawn_count = min(missing_enemies, random.randint(1, MAX_SPAWN_BATCH))
        for _ in range(spawn_count):
            enemies.append(_spawn_enemy(
                map_width,
                map_height,
                assets,
                now - game_start_ms,
                post_boss=(boss_defeated_ms is not None),
                allow_mago=mago_count() < MAX_MAGOS_NA_ARENA,
            ))

        next_spawn_ms = now + current_spawn_interval(now)

    def kill_enemy(enemy):
        nonlocal boss_defeated_ms, next_spawn_ms

        if enemy.kind in ('mago', ENEMY_MAGO_EVO, 'mago_space'):
            death_sound = SFX_MAGE_DEATH
        elif enemy.kind == ENEMY_MINOTAURO:
            death_sound = SFX_MINOTAUR_DEATH
        elif enemy.kind in (ENEMY_LEAO, ENEMY_LEAO_EVO, 'leao_space'):
            death_sound = SFX_LION_DEATH
        elif enemy.kind in ('lobisomem', ENEMY_LOBISOMEM_EVO, 'lobisomem_space'):
            death_sound = SFX_MONSTER_DEATH
        else:
            death_sound = SFX_ENEMY_DEATH

        if enemy.kind == ENEMY_MINOTAURO:
            _play_sound(assets[death_sound], repeats=5)
        else:
            _play_sound(assets[death_sound])
        player.coins += enemy.coins_reward
        player.score += enemy.coins_reward
        enemies.remove(enemy)
        contact_damage_cooldowns.pop(id(enemy), None)
        if enemy.kind == ENEMY_MINOTAURO:
            boss_defeated_ms = pygame.time.get_ticks()
            next_spawn_ms = boss_defeated_ms + POST_BOSS_RESUME_DELAY_MS
            player.max_health = 300
            player.health = player.max_health
            return f'Chefão Minotauro derrotado! +{enemy.coins_reward} moedas'
        return f'+{enemy.coins_reward} moedas'

    while running:
        clock.tick(FPS)
        buy_requested = False
        shop_slot_pressed = None
        shop_upgrade_pressed = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = QUIT
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_j, pygame.K_SPACE):
                    if not shop_open:
                        if player.start_attack():
                            attack_hit_enemies.clear()
                            if player.weapon == 'Espada':
                                assets[SFX_SWORD].play()
                            message = 'Ataque!'
                            message_timer = pygame.time.get_ticks() + 400
                if event.key == pygame.K_e:
                    buy_requested = True
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                    if event.mod & pygame.KMOD_SHIFT:
                        shop_upgrade_pressed = idx
                    else:
                        shop_slot_pressed = idx
                if event.key == pygame.K_RETURN:
                    state = QUIT
                    running = False
                if event.key == pygame.K_F1:  # pula para fase espacial
                    transition_done = True
                    transition_cap = None
                    current_background = background_fogo
                    enemies.clear()
                    boss_spawned = True
                    boss_defeated_ms = pygame.time.get_ticks()
                if event.key == pygame.K_F2:  # pula para fase de fogo
                    transition_done = False
                    transition_cap = None
                    current_background = background_arena
                    enemies.clear()
                    boss_spawned = False
                    game_start_ms = pygame.time.get_ticks() - EVO_SPAWN_START_MS


            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                mouse_pos = pygame.mouse.get_pos()
                center_screen = (LARGURA_TELA // 2, ALTURA_TELA // 2)

                if event.button == 3 and bow_ready_on_right_click():
                    shoot_arrow(mouse_pos)
                    message = 'Flecha lancada!'
                    message_timer = pygame.time.get_ticks() + 400
                elif event.button == 1:
                    if player.weapon == 'Arco':
                        shoot_arrow(mouse_pos)
                        message = 'Flecha lancada!'
                        message_timer = pygame.time.get_ticks() + 400
                        continue

                    attack_dir = player.direction_from_mouse(mouse_pos, center_screen)
                    if player.start_attack(attack_dir):
                        attack_hit_enemies.clear()
                        if player.weapon == 'Espada':
                            assets[SFX_SWORD].play()
                        message = 'Ataque!'
                        message_timer = pygame.time.get_ticks() + 400
        keys = pygame.key.get_pressed()
        player.dx = 0
        player.dy = 0

        if keys[pygame.K_a]:
            player.dx -= player.speed
        if keys[pygame.K_d]:
            player.dx += player.speed
        if keys[pygame.K_w]:
            player.dy -= player.speed
        if keys[pygame.K_s]:
            player.dy += player.speed

        player.update()
        vcamerax = player.x - LARGURA_TELA // 2
        vcameray = player.y - ALTURA_TELA // 2

        # vcamerax = max(0, min(vcamerax, map_width - LARGURA_TELA))
        # vcameray = max(0, min(vcameray, map_height - ALTURA_TELA))

        # Equipar arma ao tocar nela.
        player_rect = _player_collision_rect(player)
        # Cabana de armas
        near_cabin = player_rect.colliderect(cabin_interact_rect)
        if near_cabin and buy_requested:
            shop_open = not shop_open

        if shop_open and not near_cabin:
            shop_open = False

        if shop_open:
            WEAPON_ORDER = ['Arco', 'Cajado', 'Espada']
            if shop_slot_pressed is not None:
                w = WEAPON_ORDER[shop_slot_pressed]
                if w not in owned_weapons:
                    price = WEAPON_BUY_PRICES[w]
                    if player.coins >= price:
                        player.coins -= price
                        owned_weapons.add(w)
                        equip_message = equip_shop_weapon(w)
                        message = f'Comprou {w}! {equip_message}'
                    else:
                        message = f'Precisa de {WEAPON_BUY_PRICES[w]} moedas!'
                else:
                    message = equip_shop_weapon(w)
                message_timer = pygame.time.get_ticks() + 1200

            if shop_upgrade_pressed is not None:
                w = WEAPON_ORDER[shop_upgrade_pressed]
                next_level = weapon_upgrades[w] + 1
                if w not in owned_weapons:
                    message = f'Compre {w} primeiro!'
                elif weapon_upgrades[w] >= 2:
                    message = f'{w} ja esta no nivel maximo!'
                elif not upgrade_unlocked(next_level):
                    message = upgrade_lock_message(next_level)
                elif player.coins >= WEAPON_UPGRADE_PRICE:
                    player.coins -= WEAPON_UPGRADE_PRICE
                    weapon_upgrades[w] += 1
                    if player.weapon == w:
                        apply_upgrade(w)
                    message = f'{w} aprimorada!'
                else:
                    message = f'Precisa de {WEAPON_UPGRADE_PRICE} moedas!'
                message_timer = pygame.time.get_ticks() + 1200

        # Atualiza inimigos.
        for enemy in enemies[:]:
            enemy.update(player)

            # MAGO LANÇA FEITIÇO
            if isinstance(enemy, Mago):
                if enemy.can_cast():
                    spell = enemy.cast_spell(
                        assets,
                        map_width // 2,
                        map_height // 2
                    )
                    spells.append(spell)

            enemy_rect = enemy.rect()

            enemy_rect = enemy.rect()
            enemy_key = id(enemy)
            if player.weapon != 'Arco' and player.attacking and enemy_key not in attack_hit_enemies and player.attack_box.colliderect(enemy_rect):
                attack_hit_enemies.add(enemy_key)
                died = enemy.take_damage(player.weapon_damage, player.weapon)

                if died:
                    message = kill_enemy(enemy)
                    message_timer = pygame.time.get_ticks() + 700
                    maintain_enemy_count()
                    
                    continue
                else:
                    assets[SFX_HIT].play()

            # Dano por contato com o player.
            player_contact_rect = _shrink_rect(player_rect, 0.75, 0.70)
            enemy_contact_rect = _enemy_collision_rect(enemy)
            enemy_damage_rect = _enemy_damage_rect(enemy)

            if enemy_damage_rect.colliderect(player_contact_rect):
                now = pygame.time.get_ticks()
                if enemy.kind == ENEMY_MINOTAURO:
                    contact_cooldown = MINOTAURO_DAMAGE_COOLDOWN_MS
                elif enemy.kind in ('lobisomem', ENEMY_LOBISOMEM_EVO, ENEMY_LEAO, ENEMY_LEAO_EVO, 'lobisomem_space', 'leao_space'):
                    contact_cooldown = LOBISOMEM_DAMAGE_COOLDOWN_MS
                else:
                    contact_cooldown = CONTACT_DAMAGE_COOLDOWN_MS
                last_contact_damage = contact_damage_cooldowns.get(enemy_key, -contact_cooldown)

                if enemy.damage > 0 and now - last_contact_damage >= contact_cooldown:
                    player.take_damage(max(1, enemy.damage // 2))
                    if enemy.kind == ENEMY_MINOTAURO:
                        damage_sound = SFX_MINOTAUR_ATTACK
                    elif enemy.kind in ('lobisomem', ENEMY_LOBISOMEM_EVO, ENEMY_LEAO, ENEMY_LEAO_EVO):
                        damage_sound = SFX_MONSTER_BITE
                    else:
                        damage_sound = SFX_HIT
                    _play_sound(assets[damage_sound], repeats=5 if enemy.kind == ENEMY_MINOTAURO else 1)
                    contact_damage_cooldowns[enemy_key] = now

                if player.health <= 0:
                    break

            _separate_characters(
                player,
                enemy,
                player_contact_rect,
                enemy_contact_rect,
                move_second=not isinstance(enemy, (Mago, Minotauro)),
            )
            player.keep_inside_arena()
            if player.attacking:
                player.update_attack_box()
            player_rect = _player_collision_rect(player)

        for i, enemy in enumerate(enemies):
            for other in enemies[i + 1:]:
                _separate_characters(
                    enemy,
                    other,
                    _enemy_collision_rect(enemy),
                    _enemy_collision_rect(other),
                    move_first=not isinstance(enemy, Mago),
                    move_second=not isinstance(other, Mago),
                )

        player_rect = _player_collision_rect(player)
        vcamerax = player.x - LARGURA_TELA // 2
        vcameray = player.y - ALTURA_TELA // 2

        if not transition_done and not transition_cap and pygame.time.get_ticks() - game_start_ms >= EVO_SPAWN_START_MS:
            transition_cap = cv2.VideoCapture(assets[VIDEO_TRANSICAO])

        if transition_done and not transition_done_alien and not transition_cap_alien and boss_defeated_ms is not None:
            transition_cap_alien = cv2.VideoCapture(assets[VIDEO_TRANSICAO_ALIEN])

        maintain_enemy_count()

        # Spawn e coleta de medkits
        now_ms = pygame.time.get_ticks()
        if now_ms >= next_medkit_ms and len(medkit_spawns) < MEDKIT_MAX:
            angle = random.uniform(0, 6.28318)
            radius = random.uniform(150, 580)
            vec = pygame.math.Vector2(1, 0).rotate_rad(angle)
            mx = map_width // 2 + int(radius * vec.x)
            my = map_height // 2 + int(radius * vec.y)
            medkit_spawns.append([mx, my])
            next_medkit_ms = now_ms + current_medkit_spawn_interval()

        for mk in medkit_spawns[:]:
            mk_rect = pygame.Rect(mk[0] - 36, mk[1] - 36, 72, 72)
            if player_rect.colliderect(mk_rect):
                heal_amount = current_medkit_heal()
                player.health = min(player.max_health, player.health + heal_amount)
                message = f'+{heal_amount} VIDA'
                message_timer = pygame.time.get_ticks() + 1000
                medkit_spawns.remove(mk)

        # Atualiza feitiços
        for spell in spells[:]:
            hit_player = spell.update(player)
            if hit_player:
                assets[SFX_FIREBALL].play()

            if not spell.alive:
                spells.remove(spell)

        for arrow in arrows[:]:
            hit_enemy, died = arrow.update(enemies, map_width // 2, map_height // 2, arena_radius=785)

            if hit_enemy:
                if died:
                    message = kill_enemy(hit_enemy)
                    message_timer = pygame.time.get_ticks() + 700
                    maintain_enemy_count()
                else:
                    assets[SFX_HIT].play()

                arrows.remove(arrow)
            elif not arrow.alive:
                arrows.remove(arrow)

        
        # Desenho
        screen.fill((0, 0, 0))

        def _draw_transition_frame(cap):
            ret, frame = cap.read()
            if not ret:
                return False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            vid_h, vid_w = frame.shape[:2]
            map_w = int(LARGURA_TELA * 2.5)
            map_h = int(ALTURA_TELA * 2.5)
            cx = max(0, int(vcamerax * vid_w / map_w))
            cy = max(0, int(vcameray * vid_h / map_h))
            cw = min(int(LARGURA_TELA * vid_w / map_w), vid_w - cx)
            ch = min(int(ALTURA_TELA * vid_h / map_h), vid_h - cy)
            cropped = frame[cy:cy + ch, cx:cx + cw]
            scaled = cv2.resize(cropped, (LARGURA_TELA, ALTURA_TELA))
            screen.blit(pygame.surfarray.make_surface(scaled.swapaxes(0, 1)), (0, 0))
            return True

        if transition_cap is not None:
            if not _draw_transition_frame(transition_cap):
                transition_cap.release()
                transition_cap = None
                transition_done = True
                current_background = background_fogo
                screen.blit(current_background, (-vcamerax, -vcameray))
        elif transition_cap_alien is not None:
            if not _draw_transition_frame(transition_cap_alien):
                transition_cap_alien.release()
                transition_cap_alien = None
                transition_done_alien = True
                current_background = background_alien
                screen.blit(current_background, (-vcamerax, -vcameray))
        else:
            screen.blit(current_background, (-vcamerax, -vcameray))

        # Desenha cabana de armas
        screen.blit(cabin_image, (cabin_rect.x - vcamerax, cabin_rect.y - vcameray))

        # Desenha medkits no chão
        for mk in medkit_spawns:
            screen.blit(medkit_img, (mk[0] - vcamerax - 36, mk[1] - vcameray - 36))
        for arrow in arrows:
            arrow.draw(screen, vcamerax, vcameray)

        # UI da loja
        if shop_open:
            panel = pygame.Surface((560, 290), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 200))
            panel_x = LARGURA_TELA // 2 - 280
            panel_y = ALTURA_TELA // 2 - 445
            screen.blit(panel, (panel_x, panel_y))
            px = panel_x + 20
            py = panel_y + 14
            _draw_text(screen, font_mid, 'BARRACA DE ARMAS', px, py)
            WEAPON_ORDER = ['Arco', 'Cajado', 'Espada']
            for i, w in enumerate(WEAPON_ORDER):
                if w in owned_weapons:
                    lvl = weapon_upgrades[w]
                    if lvl >= 2:
                        status = 'MAX (Espacial)'
                        cor = (120, 180, 255)
                    elif not upgrade_unlocked(lvl + 1):
                        status = 'Especial em 1min10s' if lvl == 0 else 'MAX antes do Minotauro'
                        cor = (160, 160, 160)
                    elif lvl == 1:
                        status = f'MAX: {WEAPON_UPGRADE_PRICE} moedas'
                        cor = (255, 220, 80)
                    else:
                        status = f'Especial: {WEAPON_UPGRADE_PRICE} moedas'
                        cor = (255, 255, 255)
                else:
                    status = f'Comprar: {WEAPON_BUY_PRICES[w]} moedas'
                    cor = (255, 255, 255)
                atalho = f'[{i+1}] Equipar  |  [Shift+{i+1}] Upgradar' if w in owned_weapons else f'[{i+1}] Comprar'
                _draw_text(screen, font_mid, f'{w}  —  {status}', px, py + 46 + i * 58, cor)
                _draw_text(screen, font_small, atalho, px + 10, py + 75 + i * 58, (140, 200, 255))
            _draw_text(screen, font_small, '[E] Fechar', px, py + 240, (160, 160, 160))
        elif near_cabin:
            shop_message = 'Aperte E para abrir a loja'
            shop_message_timer = pygame.time.get_ticks() + 200


        for enemy in enemies:
            frame = enemy.get_current_frame()
            if enemy.hit_flash > pygame.time.get_ticks() > 0:
                tint = frame.copy()
                tint.fill((255, 70, 70), special_flags=pygame.BLEND_RGBA_MULT)
                frame = tint
            screen.blit(frame, (enemy.x - vcamerax - frame.get_width() // 2, enemy.y - vcameray - frame.get_height() // 2))

        # DESENHA OS FEITIÇOS AQUI
        for spell in spells:
            spell.draw(screen, vcamerax, vcameray)

        

        player_frame = player.get_current_frame()
        if player.hit_flash > pygame.time.get_ticks() > 0:
            player_frame = _tint_sprite_pixels(player_frame, (255, 70, 70))
        largura_boneco = player_frame.get_width()
        altura_boneco = player_frame.get_height()
        # player_frame = pygame.transform.smoothscale(player_frame, (int(largura_boneco * 1.25), int(altura_boneco * 1.25)))
        cx = LARGURA_TELA // 2 - player_frame.get_width() // 2
        cy = ALTURA_TELA // 2 - player_frame.get_height() // 2
       

        if player.weapon_image:
            weapon_img = pygame.transform.smoothscale(
                player.weapon_image,
                (player.weapon_image.get_width(), player.weapon_image.get_height())
            )

            player_center_x = cx + player_frame.get_width() // 2
            player_center_y = cy + player_frame.get_height() // 2

            weapon_img, weapon_rect = posiciona_arma(player, player_center_x, player_center_y, weapon_img)
            if player.direction in ['right','down_right','down']:
                screen.blit(player_frame, (cx, cy))
            
            screen.blit(weapon_img, weapon_rect.topleft)

            if player.direction not in ['right','down_right','down']:
                screen.blit(player_frame, (cx, cy))
        else:
            screen.blit(player_frame, (cx, cy))

        # HUD
        hud = pygame.Surface((760, 220), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 140))
        screen.blit(hud, (18, 18))
        _draw_text(screen, font_mid, f'Vida: {player.health}/{player.max_health}', 30, 28)
        _draw_text(screen, font_mid, f'Moedas: {player.coins}', 30, 62)
        _draw_text(screen, font_mid, f'Pontos: {player.score}', 30, 96)
        weapon_label = f'Arma: {player.weapon}'
        if bow_ready_on_right_click():
            weapon_label += ' | Direito: Arco'
        _draw_text(screen, font_small, weapon_label, 30, 130)
        attack_hint = 'Atacar: Mouse esquerdo'
        if bow_ready_on_right_click():
            attack_hint += ' | Arco: Mouse direito'
        _draw_text(screen, font_small, f'Mover: WASD | {attack_hint}', 30, 158)

        if message_timer > pygame.time.get_ticks():
            msg = font_mid.render(message, True, (255, 240, 120))
            screen.blit(msg, (LARGURA_TELA // 2 - msg.get_width() // 2, 30))
        if shop_message_timer > pygame.time.get_ticks():
            msg = font_mid.render(shop_message, True, (255, 240, 120))
            screen.blit(msg, (LARGURA_TELA // 2 - msg.get_width() // 2, 60))

        if player.health <= 0:
            state = _show_defeat_screen(screen, player_name, player.score)
            running = False

        pygame.display.flip()

    return state
