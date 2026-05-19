import random
import pygame
from config import *
from assets_loader import *
from sprites import *

spells = []

def _draw_text(screen, font, text, x, y, color=(255, 255, 255)):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))



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
    
def posiciona_arma(player, player_center_x, player_center_y, weapon_img):
    # Cada entrada: (offset_x, offset_y, rotacao)
    config = {
        'Espada': {
            'parado': {
                'right':      ( 15,   3,   -30), 'left':      ( 2, -32,  90), 'up':      ( 40, -15,  45), 'down':      (-20,  12, -90),
                'up_right':   ( 38,   5,   0), 'up_left':   ( 18 , -18,  90), 'down_right': ( -18, 17 , -90), 'down_left': (-24,  -4,  180),
            },
            'atacando': {
                'right':      ( 30, 6,   -30), 'left':      (-30, -10, 120), 'up':      (  0, -50,  45), 'down':      ( -2,  45, -90),
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
    clock = pygame.time.Clock()
    background_arena = assets[ARENA_COLISEU]
    map_width = background_arena.get_width()
    map_height = background_arena.get_height()

    player = Player(map_width, map_height, assets)

    font_small = pygame.font.SysFont('arial', 24, bold=True)
    font_mid = pygame.font.SysFont('arial', 32, bold=True)

    weapon_pickups = [
        WeaponPickup(map_width // 2 - 180, map_height // 2 + 130, assets[WEAPON_ESPADA], 'Espada', price=30),
        WeaponPickup(map_width // 2 + 220, map_height // 2 - 120, assets[WEAPON_ARCO], 'Arco', price=10),
        WeaponPickup(map_width // 2 + 40, map_height // 2 + 220, assets[WEAPON_CAJADO], 'Cajado', price=20),
    ]

    TARGET_ENEMIES = 4
    enemies = [
        _spawn_enemy(map_width, map_height, assets, player.x, player.y)
        for _ in range(TARGET_ENEMIES)
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

    def maintain_enemy_count():
        while len(enemies) < TARGET_ENEMIES:
            enemies.append(_spawn_enemy(map_width, map_height, assets, player.x, player.y))

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
        player_rect = pygame.Rect(player.x - 18, player.y - 34, 36, 68)
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
            if player.attacking and player.attack_box.colliderect(enemy_rect):
                died = enemy.take_damage(player.weapon_damage)
                if died:
                    player.coins += enemy.coins_reward
                    enemies.remove(enemy)
                    message = f'+{enemy.coins_reward} moedas'
                    message_timer = pygame.time.get_ticks() + 700
                    maintain_enemy_count()
                    
                    continue

            # Dano por contato com o player.
            if enemy_rect.colliderect(player_rect):
                if pygame.time.get_ticks() % 20 < 10:
                    player.health -= 1
                if player.health <= 0:
                    state = INIT
                    running = False
                    break

        maintain_enemy_count()

        # Atualiza feitiços
        for spell in spells[:]:
            spell.update(player)

            if not spell.alive:
                spells.remove(spell)

        # Desenho
        screen.fill((0, 0, 0))
        screen.blit(background_arena, (-vcamerax, -vcameray))
        for pickup in weapon_pickups:
            show_hint = player_rect.colliderect(pickup.rect)
            pickup.draw(screen, vcamerax, vcameray, show_hint=show_hint)


        for enemy in enemies:
            frame = enemy.get_current_frame()
            if enemy.hit_flash > pygame.time.get_ticks() > 0:
                tint = frame.copy()
                tint.fill((255, 100, 100, 120), special_flags=pygame.BLEND_RGBA_ADD)
                frame = tint
            screen.blit(frame, (enemy.x - vcamerax - frame.get_width() // 2, enemy.y - vcameray - frame.get_height() // 2))

        # DESENHA OS FEITIÇOS AQUI
        for spell in spells:
            spell.draw(screen, vcamerax, vcameray)

        if player.attacking and player.attack_box.width > 0:
            debug_box = pygame.Rect(
                player.attack_box.x - vcamerax,
                player.attack_box.y - vcameray,
                player.attack_box.width,
                player.attack_box.height,
            )
            pygame.draw.rect(screen, (255, 215, 0), debug_box, 2)

        player_frame = player.get_current_frame()
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
            screen.blit(weapon_img, weapon_rect.topleft)

        # HUD
        hud = pygame.Surface((460, 155), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 140))
        screen.blit(hud, (18, 18))
        _draw_text(screen, font_mid, f'Vida: {player.health}/{player.max_health}', 30, 28)
        _draw_text(screen, font_mid, f'Moedas: {player.coins}', 30, 62)
        _draw_text(screen, font_small, f'Arma: {player.weapon}', 30, 100)
        _draw_text(screen, font_small, 'Mover: WASD | Atacar: J ou ESPACO', 30, 128)
        screen.blit(player_frame, (cx, cy))

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
