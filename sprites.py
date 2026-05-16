import math
import random
import pygame



def cortar_spritesheet(sheet, frame_w, frame_h, max_colunas=None):
    animacoes = []

    total_colunas = sheet.get_width() // frame_w
    total_linhas = sheet.get_height() // frame_h

    if max_colunas is None:
        max_colunas = total_colunas

    for y in range(total_linhas):
        linha = []
        for x in range(max_colunas):
            frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (x * frame_w, y * frame_h, frame_w, frame_h))
            linha.append(frame)
        animacoes.append(linha)

    return animacoes



def _scale_frames(frames, scale_factor):
    scaled = []
    for frame in frames:
        w, h = frame.get_size()
        if scale_factor != 1:
            frame = pygame.transform.smoothscale(frame, (max(1, int(w * scale_factor)), max(1, int(h * scale_factor))))
        scaled.append(frame)
    return scaled


class Player:
    def __init__(self, map_width, map_height, assets):
        self.x = map_width // 2
        self.y = map_height // 2
        self.mapwidth = map_width
        self.mapheight = map_height
        self.speed = 5
        self.dx = 0
        self.dy = 0
        self.sheet = assets['player_sheet']

        frame_w = self.sheet.get_width() // 8
        frame_h = self.sheet.get_height() // 8
        frames = cortar_spritesheet(self.sheet, frame_w, frame_h)

        self.animacoes = {
            'down': frames[6],
            'left': frames[1],
            'right': frames[3],
            'up': frames[2],
        }

        # A primeira fileira funciona bem como animacao de ataque/soco.
        self.attack_frames = {
            'down': frames[0],
            'left': frames[0],
            'right': frames[0],
            'up': frames[0],
        }

        self.direction = 'down'
        self.frame_timer = 0

        self.health = 100
        self.max_health = 100
        self.coins = 0
        self.weapon = 'Punhos'
        self.weapon_damage = 1
        self.attack_range = 48
        self.attack_cooldown_ms = 320
        self.attack_duration_ms = 140
        self.last_attack_ms = 0
        self.attack_start_ms = 0
        self.attacking = False
        self.attack_direction = self.direction
        self.attack_box = pygame.Rect(0, 0, 0, 0)
        self.weapon_image = None
        self.weapon_images = {
            'Espada': assets.get('weapon_espada'),
            'Arco': assets.get('weapon_arco'),
            'Cajado': assets.get('weapon_cajado'),
        }

    def equip(self, weapon_name):
        weapons = {
            'Espada': {'damage': 3, 'range': 66},
            'Arco': {'damage': 2, 'range': 140},
            'Cajado': {'damage': 4, 'range': 90},
            'Punhos': {'damage': 1, 'range': 48},
        }
        weapon = weapons.get(weapon_name, weapons['Punhos'])
        self.weapon = weapon_name
        self.weapon_damage = weapon['damage']
        self.attack_range = weapon['range']
        self.weapon_image = self.weapon_images.get(weapon_name)

    def can_attack(self):
        return pygame.time.get_ticks() - self.last_attack_ms >= self.attack_cooldown_ms

    def start_attack(self):
        now = pygame.time.get_ticks()
        if not self.can_attack():
            return False
        self.last_attack_ms = now
        self.attack_start_ms = now
        self.attacking = True
        self.attack_direction = self.direction
        self.update_attack_box()
        return True

    def update_attack_box(self):
        box_size = self.attack_range
        if self.attack_direction == 'up':
            self.attack_box = pygame.Rect(self.x - box_size // 2, self.y - box_size, box_size, box_size)
        elif self.attack_direction == 'down':
            self.attack_box = pygame.Rect(self.x - box_size // 2, self.y + 10, box_size, box_size)
        elif self.attack_direction == 'left':
            self.attack_box = pygame.Rect(self.x - box_size, self.y - box_size // 2, box_size, box_size)
        else:
            self.attack_box = pygame.Rect(self.x + 10, self.y - box_size // 2, box_size, box_size)

    def update(self):
        self.old_x = self.x
        self.old_y = self.y

        self.x += self.dx
        self.y += self.dy

        distancia_centro = math.dist((self.x, self.y), (self.mapwidth // 2, self.mapheight // 2))

        if distancia_centro > 785 or (self.y - self.mapheight // 2) < -625:
            self.x = self.old_x
            self.y = self.old_y

        moving = (self.dx != 0 or self.dy != 0)

        if moving:
            if abs(self.dx) > abs(self.dy):
                self.direction = 'right' if self.dx > 0 else 'left'
            else:
                self.direction = 'down' if self.dy > 0 else 'up'

            self.frame_timer += 0.15
            if self.frame_timer >= len(self.animacoes[self.direction]):
                self.frame_timer = 0
        else:
            self.frame_timer = 0

        if self.attacking:
            self.update_attack_box()
            if pygame.time.get_ticks() - self.attack_start_ms > self.attack_duration_ms:
                self.attacking = False
                self.attack_box = pygame.Rect(0, 0, 0, 0)

    def get_current_frame(self):
        frames = self.attack_frames[self.attack_direction] if self.attacking else self.animacoes[self.direction]
        frame_index = int(self.frame_timer) % len(frames)
        return frames[frame_index]


class Enemy:
    def __init__(self, x, y, assets, kind='esqueleto'):
        self.kind = kind
        self.sheet = assets[kind]
        frame_w = self.sheet.get_width() // 8
        frame_h = self.sheet.get_height() // 8
        frames = cortar_spritesheet(self.sheet, frame_w, frame_h)

        # Inimigos maiores para ficarem visiveis na arena.
        scale_factor = 1.0
        self.animacoes = {
            'down': _scale_frames(frames[6], scale_factor),
            'left': _scale_frames(frames[1], scale_factor),
            'right': _scale_frames(frames[3], scale_factor),
            'up': _scale_frames(frames[2], scale_factor),
        }
        self.direction = 'down'
        self.frame_timer = 0
        self.frame_speed = 0.12
        self.x = float(x)
        self.y = float(y)
        self.speed = random.randint(2, 4)
        self.max_health = random.randint(2, 4)
        self.health = self.max_health
        self.damage = 10
        self.coins_reward = random.randint(1, 3)
        self.hit_flash = 0

    def rect(self):
        frame = self.get_current_frame()
        return frame.get_rect(center=(int(self.x), int(self.y)))

    def get_current_frame(self):
        frames = self.animacoes[self.direction]
        return frames[int(self.frame_timer) % len(frames)]

    def update(self, player):
        now = pygame.time.get_ticks()
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            step = self.speed
            self.x += step * dx / dist
            self.y += step * dy / dist

            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'

            self.frame_timer += self.frame_speed

        if self.hit_flash > 0 and now >= self.hit_flash:
            self.hit_flash = 0

    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = pygame.time.get_ticks() + 120
        return self.health <= 0

class WeaponPickup:
    def __init__(self, x, y, image, name):
        self.name = name

        rect = image.get_bounding_rect()
        if rect.width > 0 and rect.height > 0:
            image = image.subsurface(rect).copy()

        self.image = pygame.transform.smoothscale(image, (80, 80))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen, cam_x, cam_y):
        sx = self.rect.x - cam_x
        sy = self.rect.y - cam_y
        pygame.draw.rect(
            screen,
            (255, 215, 0),
            (sx - 4, sy - 4, self.rect.w + 8, self.rect.h + 8),
            2
        )
        screen.blit(self.image, (sx, sy))
# class WeaponPickup:antes tava assim
#     def __init__(self, x, y, image, name):
#         self.name = name
#         self.image = pygame.transform.smoothscale(image, (140, 140))
#         self.rect = self.image.get_rect(center=(x, y))

#     def draw(self, screen, cam_x, cam_y):
#         sx = self.rect.x - cam_x
#         sy = self.rect.y - cam_y
#         pygame.draw.rect(screen, (255, 215, 0), (sx - 8, sy - 8, self.rect.w + 16, self.rect.h + 16), 3)
#         screen.blit(self.image, (sx, sy))
