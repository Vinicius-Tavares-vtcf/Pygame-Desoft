import random
import pygame
from config import *
from assets_loader import *
from sprites import *

spells = []

def _draw_text(screen, font, text, x, y, color=(255, 255, 255)):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


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
        return _shrink_rect(enemy.rect(), 0.26, 0.30)
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


def _spawn_enemy(map_width, map_height, assets, player_x, player_y):
    enemy_type = random.choice(['esqueleto', 'lobisomem', 'mago'])

    if enemy_type == 'mago':
        centro_x = map_width // 2
        centro_y = map_height // 2
        raio = 760

        lado = random.choice(['left', 'right', 'up', 'down'])

        if lado == 'left':
            x = centro_x - raio - 100
            y = random.randint(centro_y - 250, centro_y + 250)
            side = 'left'
        elif lado == 'right':
            x = centro_x + raio + 100
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

        return Mago(x, y, assets, side=side)

    angle = random.uniform(0, 6.28318)
    distance = random.randint(240, 520)
    x = player_x + int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
    y = player_y + int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
    x = max(100, min(x, map_width - 100))
    y = max(100, min(y, map_height - 100))

    if enemy_type == 'esqueleto':
        return Esqueleto(x, y, assets)
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



def game_screen(screen, assets):
    pygame.mixer.music.load(assets[MUSICA_MIDGAME])
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    background_arena = assets[ARENA_COLISEU]
    map_width = background_arena.get_width()
    map_height = background_arena.get_height()

    player = Player(map_width, map_height, assets)

    # Caixa de Cura
    heal_price = 25
    heal_amount = 50
    heal_image = assets[MEDKIT]
    heal_rect = heal_image.get_rect(center=(map_width // 2 + 590, map_height // 2 - 430))

    font_small = pygame.font.SysFont('arial', 24, bold=True)
    font_mid = pygame.font.SysFont('arial', 32, bold=True)

    weapon_pickups = [
        WeaponPickup(map_width // 2 - 180, map_height // 2 + 130, assets[WEAPON_ESPADA], 'Espada', price=40),
        WeaponPickup(map_width // 2 + 220, map_height // 2 - 120, assets[WEAPON_ARCO], 'Arco', price=10),
        WeaponPickup(map_width // 2 + 40, map_height // 2 + 220, assets[WEAPON_CAJADO], 'Cajado', price=15),
    ]

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
    POST_BOSS_RESUME_DELAY_MS = 10_000
    POST_BOSS_BASE_WAVE_SIZE = 20
    POST_BOSS_GROWTH_INTERVAL_MS = 10_000
    max_wave_reached_ms = (
        WAVE_FIRST_GROWTH_MS
        + ((MAX_WAVE_SIZE - BASE_WAVE_SIZE) // WAVE_GROWTH_AMOUNT - 1) * WAVE_GROWTH_INTERVAL_MS
    )
    game_start_ms = pygame.time.get_ticks()
    next_spawn_ms = game_start_ms + SPAWN_INTERVAL_MS
    boss_spawned = False
    boss_defeated_ms = None

    initial_enemy_count = min(MAX_SPAWN_BATCH, BASE_WAVE_SIZE)
    enemies = [
        _spawn_enemy(map_width, map_height, assets, player.x, player.y)
        for _ in range(initial_enemy_count)
    ]
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

        growth_steps = 1 + (elapsed - WAVE_FIRST_GROWTH_MS) // WAVE_GROWTH_INTERVAL_MS
        return min(MAX_WAVE_SIZE, BASE_WAVE_SIZE + growth_steps * WAVE_GROWTH_AMOUNT)

    def current_spawn_interval(now):
        if now - game_start_ms >= FAST_SPAWN_START_MS:
            return FAST_SPAWN_INTERVAL_MS
        return SPAWN_INTERVAL_MS

    def normal_enemy_count():
        return sum(1 for enemy in enemies if not isinstance(enemy, Minotauro))

    def boss_alive():
        return any(isinstance(enemy, Minotauro) for enemy in enemies)

    def maintain_enemy_count():
        nonlocal next_spawn_ms, boss_spawned

        now = pygame.time.get_ticks()
        boss_spawn_ms = game_start_ms + max_wave_reached_ms + BOSS_SPAWN_DELAY_AFTER_MAX_WAVE_MS
        if not boss_spawned and now >= boss_spawn_ms:
            enemies.append(_spawn_boss(map_width, map_height, assets))
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
            enemies.append(_spawn_enemy(map_width, map_height, assets, player.x, player.y))

        next_spawn_ms = now + current_spawn_interval(now)

    def kill_enemy(enemy):
        nonlocal boss_defeated_ms, next_spawn_ms

        if enemy.kind == 'mago':
            death_sound = SFX_MAGE_DEATH
        elif enemy.kind == ENEMY_MINOTAURO:
            death_sound = SFX_MINOTAUR_DEATH
        elif enemy.kind == 'lobisomem':
            death_sound = SFX_MONSTER_DEATH
        else:
            death_sound = SFX_ENEMY_DEATH

        death_channel = pygame.mixer.find_channel(True)
        if death_channel:
            death_channel.play(assets[death_sound])
        else:
            assets[death_sound].play()
        player.coins += enemy.coins_reward
        enemies.remove(enemy)
        contact_damage_cooldowns.pop(id(enemy), None)
        if enemy.kind == ENEMY_MINOTAURO:
            boss_defeated_ms = pygame.time.get_ticks()
            next_spawn_ms = boss_defeated_ms + POST_BOSS_RESUME_DELAY_MS
            return f'Chefão Minotauro derrotado! +{enemy.coins_reward} moedas'
        return f'+{enemy.coins_reward} moedas'

    while running:
        clock.tick(FPS)
        buy_requested = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = QUIT
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_j, pygame.K_SPACE):
                    if player.start_attack():
                        attack_hit_enemies.clear()
                        if player.weapon == 'Espada':
                            assets[SFX_SWORD].play()
                        message = 'Ataque!'
                        message_timer = pygame.time.get_ticks() + 400
                # Compra da arma
                if event.key == pygame.K_k:
                    buy_requested = True

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
        remaining_pickups = []
        pickup_em_cima = None

        for pickup in weapon_pickups:
            if player_rect.colliderect(pickup.rect):
                shop_message = f'{pickup.price} moedas | Aperte K para comprar'
                shop_message_timer = pygame.time.get_ticks() + 200

                if buy_requested:
                    if player.coins >= pickup.price:
                        player.coins -= pickup.price
                        player.equip(pickup.name, pickup.equip_sheet)
                        message = f'Comprou {pickup.name} por {pickup.price} moedas!'
                        message_timer = pygame.time.get_ticks() + 1200
                        continue
                    else:
                        message = f'Precisa de {pickup.price} moedas!'
                        message_timer = pygame.time.get_ticks() + 1200

            remaining_pickups.append(pickup)

        weapon_pickups = remaining_pickups

        if player_rect.colliderect(heal_rect):
            shop_message = f'{heal_price} moedas | Aperte K para curar'
            shop_message_timer = pygame.time.get_ticks() + 200

            if buy_requested:
                if player.health >= player.max_health:
                    message = 'Vida cheia!'
                    message_timer = pygame.time.get_ticks() + 1200
                elif player.coins >= heal_price:
                    player.coins -= heal_price
                    player.health = min(player.max_health, player.health + heal_amount)
                    message = f'+{heal_amount} VIDA'
                    message_timer = pygame.time.get_ticks() + 1200
                else:
                    message = 'Moedas insuficientes!'
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
            if player.attacking and enemy_key not in attack_hit_enemies and player.attack_box.colliderect(enemy_rect):
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

            if enemy_contact_rect.colliderect(player_contact_rect):
                now = pygame.time.get_ticks()
                if enemy.kind == ENEMY_MINOTAURO:
                    contact_cooldown = MINOTAURO_DAMAGE_COOLDOWN_MS
                elif enemy.kind == 'lobisomem':
                    contact_cooldown = LOBISOMEM_DAMAGE_COOLDOWN_MS
                else:
                    contact_cooldown = CONTACT_DAMAGE_COOLDOWN_MS
                last_contact_damage = contact_damage_cooldowns.get(enemy_key, -contact_cooldown)

                if enemy.damage > 0 and now - last_contact_damage >= contact_cooldown:
                    player.take_damage(enemy.damage)
                    if enemy.kind == ENEMY_MINOTAURO:
                        damage_sound = SFX_MINOTAUR_ATTACK
                    elif enemy.kind == 'lobisomem':
                        damage_sound = SFX_MONSTER_BITE
                    else:
                        damage_sound = SFX_HIT
                    assets[damage_sound].play()
                    contact_damage_cooldowns[enemy_key] = now

                if player.health <= 0:
                    state = INIT
                    running = False
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

        maintain_enemy_count()

        # Atualiza feitiços
        for spell in spells[:]:
            hit_player = spell.update(player)
            if hit_player:
                assets[SFX_FIREBALL].play()

            if not spell.alive:
                spells.remove(spell)

        # Desenho
        screen.fill((0, 0, 0))
        screen.blit(background_arena, (-vcamerax, -vcameray))

        # Desenha caixa de cura
        screen.blit(
            heal_image,
            (heal_rect.x - vcamerax, heal_rect.y - vcameray)
        )

        for pickup in weapon_pickups:
            show_hint = player_rect.colliderect(pickup.rect)
            pickup.draw(screen, vcamerax, vcameray, show_hint=show_hint)


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
       

        # Desenha a arma equipada na mao do personagem.
        '''if player.weapon_image:
            weapon_img = pygame.transform.smoothscale(player.weapon_image, (92, 92))
            if player.direction == 'right':
                screen.blit(weapon_img, (cx + 26, cy + 18))
            elif player.direction == 'left':
                weapon_img = pygame.transform.flip(weapon_img, True, False)
                screen.blit(weapon_img, (cx - 40, cy + 18))
            elif player.direction == 'up':
                weapon_img = pygame.transform.rotate(weapon_img, 90)
                screen.blit(weapon_img, (cx + 10, cy - 30))
            else:
                weapon_img = pygame.transform.rotate(weapon_img, -90)
                screen.blit(weapon_img, (cx + 10, cy + 32))'''
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
        hud = pygame.Surface((460, 155), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 140))
        screen.blit(hud, (18, 18))
        _draw_text(screen, font_mid, f'Vida: {player.health}/{player.max_health}', 30, 28)
        _draw_text(screen, font_mid, f'Moedas: {player.coins}', 30, 62)
        _draw_text(screen, font_small, f'Arma: {player.weapon}', 30, 100)
        _draw_text(screen, font_small, 'Mover: WASD | Atacar: J ou ESPACO', 30, 128)

        if message_timer > pygame.time.get_ticks():
            msg = font_mid.render(message, True, (255, 240, 120))
            screen.blit(msg, (LARGURA_TELA // 2 - msg.get_width() // 2, 30))
        if shop_message_timer > pygame.time.get_ticks():
            msg = font_mid.render(shop_message, True, (255, 240, 120))
            screen.blit(msg, (LARGURA_TELA // 2 - msg.get_width() // 2, 60))

        if player.health <= 0:
            state = INIT
            running = False

        pygame.display.flip()

    return state
