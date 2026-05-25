import math
import random
import pygame
from assets_loader import *
def melhor_frame_visivel(sheet, grid=8):
    frame_w = sheet.get_width() // grid
    frame_h = sheet.get_height() // grid
    frames = cortar_spritesheet(sheet, frame_w, frame_h)

    melhor = None
    melhor_area = -1

    for linha in frames:
        for frame in linha:
            rect = frame.get_bounding_rect()
            area = rect.width * rect.height
            if area > melhor_area:
                melhor_area = area
                melhor = frame.subsurface(rect).copy() if area > 0 else frame

    return melhor if melhor is not None else pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)


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


def _trim_frame(frame):
    rect = frame.get_bounding_rect()
    if rect.width == 0 or rect.height == 0:
        return frame
    return frame.subsurface(rect).copy()


def pegar_frame(sheet, linha, coluna, grid=32):
    frame_w = sheet.get_width() // grid
    frame_h = sheet.get_height() // grid

    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
    frame.blit(
        sheet,
        (0, 0),
        (coluna * frame_w, linha * frame_h, frame_w, frame_h)
    )

    rect = frame.get_bounding_rect()

    if rect.width > 0 and rect.height > 0:
        frame = frame.subsurface(rect).copy()

    return frame


def _scale_frames(frames, scale_factor, smooth=True):
    scaled = []
    for frame in frames:
        w, h = frame.get_size()
        if scale_factor != 1:
            size = (max(1, int(w * scale_factor)), max(1, int(h * scale_factor)))
            if smooth:
                frame = pygame.transform.smoothscale(frame, size)
            else:
                frame = pygame.transform.scale(frame, size)
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

        scale_factor = 1.1

        self.animacoes = {
            'down':       _scale_frames(frames[6][:4], scale_factor),
            'left':       _scale_frames(frames[0][:4], scale_factor),
            'right':      _scale_frames(frames[4][:4], scale_factor),
            'up':         _scale_frames(frames[1][:4], scale_factor),
            'up_left':    _scale_frames(frames[1][:4], scale_factor),
            'up_right':   _scale_frames(frames[3][:4], scale_factor),
            'down_right': _scale_frames(frames[5][:4], scale_factor),
            'down_left':  _scale_frames(frames[7][:4], scale_factor),
        }

        self.attack_frames = {
            'down':       frames[6],
            'left':       frames[0],
            'right':      frames[4],
            'up':         frames[1],
            'up_left':    frames[1],
            'up_right':   frames[3],
            'down_right': frames[5],
            'down_left':  frames[7],
        }

        self.direction = 'down'
        self.frame_timer = 0

        self.health = 100
        self.max_health = 100
        self.coins = 0
        self.score = 0
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
        self.hit_flash = 0


    '''def equip(self, weapon_name): #Troca a arma do jogador e ajusta dano, alcance e imagem da arma.
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
        self.weapon_image = self.weapon_images.get(weapon_name)'''
    def direction_from_mouse(self, mouse_pos, screen_center): #Descobre a direção do mouse, dividindo o círculo em 8 fatias.
        dx = mouse_pos[0] - screen_center[0]
        dy = mouse_pos[1] - screen_center[1]

        angle = math.degrees(math.atan2(-dy, dx))

        if -22.5 <= angle < 22.5:
            return 'right'
        elif 22.5 <= angle < 67.5:
            return 'up_right'
        elif 67.5 <= angle < 112.5:
            return 'up'
        elif 112.5 <= angle < 157.5:
            return 'up_left'
        elif angle >= 157.5 or angle < -157.5:
            return 'left'
        elif -157.5 <= angle < -112.5:
            return 'down_left'
        elif -112.5 <= angle < -67.5:
            return 'down'
        else:
            return 'down_right'
    def equip(self, weapon_name, weapon_sheet=None, weapon_frame=None):
        weapons = {
            'Espada': {'damage': 4, 'range': 66},
            'Arco': {'damage': 2, 'range': 140},
            'Cajado': {'damage': 3, 'range': 80},
            'Punhos': {'damage': 1, 'range': 48},
        }

        weapon = weapons.get(weapon_name, weapons['Punhos'])
        self.weapon = weapon_name
        self.weapon_damage = weapon['damage']
        self.attack_range = weapon['range']

        if weapon_frame is not None:
            self.weapon_image = weapon_frame
        elif weapon_sheet is not None:
            self.weapon_image = melhor_frame_visivel(weapon_sheet, grid=8)
        else:
            self.weapon_image = None

    def can_attack(self): # Verifica se já passou tempo suficiente para atacar de novo.
        return pygame.time.get_ticks() - self.last_attack_ms >= self.attack_cooldown_ms

    def start_attack(self, attack_direction=None):
        now = pygame.time.get_ticks()
        if not self.can_attack():
            return False

        self.last_attack_ms = now
        self.attack_start_ms = now
        self.attacking = True

        self.attack_direction = attack_direction if attack_direction else self.direction

        # PLAYER OLHA PARA O ATAQUE
        self.direction = self.attack_direction

        self.update_attack_box()
        return True

    def update_attack_box(self):
        s = self.attack_range
        h = s // 2
        d = self.attack_direction
        if d == 'up':
            self.attack_box = pygame.Rect(self.x - h,  self.y - s,  s, s)
        elif d == 'down':
            self.attack_box = pygame.Rect(self.x - h,  self.y + 10, s, s)
        elif d == 'left':
            self.attack_box = pygame.Rect(self.x - s,  self.y - h,  s, s)
        elif d == 'right':
            self.attack_box = pygame.Rect(self.x + 10, self.y - h,  s, s)
        elif d == 'up_right':
            self.attack_box = pygame.Rect(self.x + 10, self.y - s,  s, s)
        elif d == 'up_left':
            self.attack_box = pygame.Rect(self.x - s,  self.y - s,  s, s)
        elif d == 'down_right':
            self.attack_box = pygame.Rect(self.x + 10, self.y + 10, s, s)
        elif d == 'down_left':
            self.attack_box = pygame.Rect(self.x - s,  self.y + 10, s, s)

    def keep_inside_arena(self):
        center_x = self.mapwidth // 2
        center_y = self.mapheight // 2
        arena_radius = 785
        arena_top = center_y - 625

        if self.y < arena_top:
            self.y = arena_top

        dx = self.x - center_x
        dy = self.y - center_y
        distance = math.hypot(dx, dy)

        if distance > arena_radius and distance > 0:
            scale = arena_radius / distance
            self.x = center_x + dx * scale
            self.y = center_y + dy * scale

    def update(self): #Atualiza o movimento, a direção, a animação e o ataque.
        now = pygame.time.get_ticks()
        self.old_x = self.x
        self.old_y = self.y

        self.x += self.dx
        self.y += self.dy

        distancia_centro = math.dist((self.x, self.y), (self.mapwidth // 2, self.mapheight // 2))

        if distancia_centro > 785 or (self.y - self.mapheight // 2) < -625:
            self.x = self.old_x
            self.y = self.old_y
            self.keep_inside_arena()

        moving = (self.dx != 0 or self.dy != 0)

        if moving:
            if self.dx != 0 and self.dy != 0:
                if   self.dx > 0 and self.dy < 0: self.direction = 'up_right'
                elif self.dx < 0 and self.dy < 0: self.direction = 'up_left'
                elif self.dx > 0 and self.dy > 0: self.direction = 'down_right'
                else:                             self.direction = 'down_left'
            elif self.dx != 0:
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
            if now - self.attack_start_ms > self.attack_duration_ms:
                self.attacking = False
                self.attack_box = pygame.Rect(0, 0, 0, 0)

        if self.hit_flash > 0 and now >= self.hit_flash:
            self.hit_flash = 0

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        self.hit_flash = pygame.time.get_ticks() + 120

    def get_current_frame(self): #Retorna o frame certo da animação no momento atual.
        if self.attacking:
            frames = self.attack_frames[self.attack_direction]
            if self.weapon == 'Arco':
                frame_index = 5
            else: frame_index = 4
        else:   
            frames = self.animacoes[self.direction]
            frame_index = int(self.frame_timer) % len(frames)
        return frames[frame_index]


class Enemy:
    KIND = ENEMY_ESQUELETO
    SPEED_RANGE = (2, 6) #estav 2,4
    HP_RANGE = (2, 4)
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 3,
        'Cajado': 2,
        'Espada': 1,
    }
    DAMAGE = 3
    COINS_RANGE = (1, 3)
    SCALE = 1.1
    FRAME_SPEED = 0.12
    ATTACK_RANGE = 150
    ATTACK_COOLDOWN_MS = 400
    ATTACK_DURATION_MS = 300

    def __init__(self, x, y, assets):
        self.kind = self.KIND
        self.sheet = assets[self.KIND]

        frame_w = self.sheet.get_width() // 8
        frame_h = self.sheet.get_height() // 8
        frames = cortar_spritesheet(self.sheet, frame_w, frame_h)

        self.animacoes = {
            'down':       _scale_frames(frames[6][:4], self.SCALE),
            'left':       _scale_frames(frames[0][:4], self.SCALE),
            'right':      _scale_frames(frames[4][:4], self.SCALE),
            'up':         _scale_frames(frames[2][:4], self.SCALE),
            'up_left':    _scale_frames(frames[1][:4], self.SCALE),
            'up_right':   _scale_frames(frames[3][:4], self.SCALE),
            'down_right': _scale_frames(frames[5][:4], self.SCALE),
            'down_left':  _scale_frames(frames[7][:4], self.SCALE),
        }

        self.attack_frames = {
            'down':       _scale_frames(frames[6], self.SCALE),
            'left':       _scale_frames(frames[0], self.SCALE),
            'right':      _scale_frames(frames[4], self.SCALE),
            'up':         _scale_frames(frames[2], self.SCALE),
            'up_left':    _scale_frames(frames[1], self.SCALE),
            'up_right':   _scale_frames(frames[3], self.SCALE),
            'down_right': _scale_frames(frames[5], self.SCALE),
            'down_left':  _scale_frames(frames[7], self.SCALE),
        }

        self.direction = 'down'
        self.frame_timer = 0
        self.x = float(x)
        self.y = float(y)
        self.speed = random.randint(*self.SPEED_RANGE)
        self.max_health = random.randint(*self.HP_RANGE)
        self.health = self.max_health
        self.hits_taken = 0
        self.damage = self.DAMAGE
        self.coins_reward = random.randint(*self.COINS_RANGE)
        self.hit_flash = 0
        self.attacking = False
        self.attack_direction = 'down'
        self.last_attack_ms = 0
        self.attack_start_ms = 0

    def rect(self):
        frame = self.get_current_frame()
        return frame.get_rect(center=(int(self.x), int(self.y)))

    def can_attack(self):
        return pygame.time.get_ticks() - self.last_attack_ms >= self.ATTACK_COOLDOWN_MS

    def start_attack(self, direction):
        now = pygame.time.get_ticks()
        self.last_attack_ms = now
        self.attack_start_ms = now
        self.attacking = True
        self.attack_direction = direction

    def get_current_frame(self):
        if self.attacking:
            frames = self.attack_frames[self.attack_direction]
            frame_index = 4
        else:
            frames = self.animacoes[self.direction]
            frame_index = int(self.frame_timer) % len(frames)
        return frames[frame_index]

    def update(self, player):
        now = pygame.time.get_ticks()
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if self.attacking and now - self.attack_start_ms > self.ATTACK_DURATION_MS:
            self.attacking = False

        if dist > 0:
            maior = max(abs(dx), abs(dy))
            if maior > 0 and min(abs(dx), abs(dy)) / maior > 0.4:
                if   dx > 0 and dy < 0: self.direction = 'up_right'
                elif dx < 0 and dy < 0: self.direction = 'up_left'
                elif dx > 0 and dy > 0: self.direction = 'down_right'
                else:                   self.direction = 'down_left'
            elif abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'

            if dist <= self.ATTACK_RANGE and self.can_attack():
                self.start_attack(self.direction)

            if not self.attacking:
                step = self.speed
                self.x += step * dx / dist
                self.y += step * dy / dist
                self.frame_timer += self.FRAME_SPEED

        if self.hit_flash > 0 and now >= self.hit_flash:
            self.hit_flash = 0

    def take_damage(self, damage, weapon_name=None):
        self.hits_taken += 1
        hits_to_die = self.HITS_TO_DIE_BY_WEAPON.get(weapon_name, self.HITS_TO_DIE_BY_WEAPON['Punhos'])
        self.health = max(0, hits_to_die - self.hits_taken)
        self.hit_flash = pygame.time.get_ticks() + 120
        return self.hits_taken >= hits_to_die


class Esqueleto(Enemy):
    KIND = 'esqueleto'
    HP_RANGE = (1, 1)
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 2,
        'Cajado': 1,
        'Espada': 1,
    }
    DAMAGE = 2
    ATTACK_RANGE = 120
    ATTACK_COOLDOWN_MS = 300
    ATTACK_DURATION_MS = 250

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)


class EsqueletoEvo(Enemy):
    KIND = ENEMY_ESQUELETO_EVO
    HP_RANGE = (2, 2)
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 4,
        'Cajado': 2,
        'Espada': 2,
    }
    DAMAGE = 4
    SPEED_RANGE = (4, 7)
    COINS_RANGE = (2, 4)
    ATTACK_RANGE = 130
    ATTACK_COOLDOWN_MS = 220
    ATTACK_DURATION_MS = 200

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)


class Lobisomem(Enemy):
    KIND = 'lobisomem'
    HP_RANGE = (5, 5)
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 5,
        'Cajado': 3,
        'Espada': 2,
    }
    DAMAGE = 5
    ATTACK_RANGE = 150
    ATTACK_COOLDOWN_MS = 1500
    ATTACK_DURATION_MS = 500

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)


class LobisomemEvo(Enemy):
    KIND = ENEMY_LOBISOMEM_EVO
    HP_RANGE = (8, 8)
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 9,
        'Cajado': 5,
        'Espada': 3,
    }
    DAMAGE = 8
    SPEED_RANGE = (3, 6)
    COINS_RANGE = (3, 6)
    ATTACK_RANGE = 160
    ATTACK_COOLDOWN_MS = 1000
    ATTACK_DURATION_MS = 500

    _TINT = (255, 100, 65)

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)
        for frames in list(self.animacoes.values()) + list(self.attack_frames.values()):
            for i, frame in enumerate(frames):
                tinted = frame.copy()
                tinted.fill(self._TINT, special_flags=pygame.BLEND_RGBA_MULT)
                frames[i] = tinted


class Leao(Enemy):
    KIND = ENEMY_LEAO
    HP_RANGE = (9, 9)
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 10,
        'Cajado': 6,
        'Espada': 4,
    }
    DAMAGE = 8
    SPEED_RANGE = (2, 3)
    COINS_RANGE = (5, 10)
    SCALE = 1.8
    ATTACK_RANGE = 170
    ATTACK_COOLDOWN_MS = 2000
    ATTACK_DURATION_MS = 700

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)


class LeaoEvo(Enemy):
    KIND = ENEMY_LEAO_EVO
    HP_RANGE = (14, 14)
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 16,
        'Cajado': 10,
        'Espada': 7,
    }
    DAMAGE = 13
    SPEED_RANGE = (3, 5)
    COINS_RANGE = (8, 15)
    SCALE = 1.8
    ATTACK_RANGE = 180
    ATTACK_COOLDOWN_MS = 1500
    ATTACK_DURATION_MS = 700

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)


class Minotauro:
    KIND = ENEMY_MINOTAURO
    HITS_TO_DIE_BY_WEAPON = {
        'Punhos': 180,
        'Cajado': 90,
        'Espada': 60,
    }
    DAMAGE = 30
    COINS_RANGE = (6, 12)
    SPEED_RANGE = (4, 8)
    SCALE = 4.0
    FRAME_SPEED = 0.10
    FRAME_COLUMNS = 24
    FRAME_ROWS = 8
    STOP_DISTANCE = 40

    def __init__(self, x, y, assets):
        self.kind = self.KIND
        self.x = float(x)
        self.y = float(y)
        self.sheet = assets[self.KIND]

        frame_w = self.sheet.get_width() // self.FRAME_COLUMNS
        frame_h = self.sheet.get_height() // self.FRAME_ROWS
        frames = cortar_spritesheet(self.sheet, frame_w, frame_h, max_colunas=self.FRAME_COLUMNS)
        frames = [[_trim_frame(frame) for frame in row] for row in frames]

        self.animacoes = {
            'down':       _scale_frames(frames[6][:12], self.SCALE, smooth=False),
            'left':       _scale_frames(frames[0][:12], self.SCALE, smooth=False),
            'right':      _scale_frames(frames[4][:12], self.SCALE, smooth=False),
            'up':         _scale_frames(frames[2][:12], self.SCALE, smooth=False),
            'up_left':    _scale_frames(frames[1][:12], self.SCALE, smooth=False),
            'up_right':   _scale_frames(frames[3][:12], self.SCALE, smooth=False),
            'down_right': _scale_frames(frames[5][:12], self.SCALE, smooth=False),
            'down_left':  _scale_frames(frames[7][:12], self.SCALE, smooth=False),
        }

        self.direction = 'down'
        self.frame_timer = 0
        self.max_health = 36
        self.health = self.max_health
        self.hits_taken = 0
        self.damage = self.DAMAGE
        self.coins_reward = random.randint(*self.COINS_RANGE)
        self.hit_flash = 0
        self.speed = random.randint(*self.SPEED_RANGE)

    def rect(self):
        frame = self.get_current_frame()
        return frame.get_rect(center=(int(self.x), int(self.y)))

    def get_current_frame(self):
        frame = self.animacoes[self.direction][int(self.frame_timer) % len(self.animacoes[self.direction])]
        if self.hit_flash > 0 and pygame.time.get_ticks() < self.hit_flash:
            tint = frame.copy()
            tint.fill((255, 70, 70), special_flags=pygame.BLEND_RGBA_MULT)
            return tint
        return frame

    def update(self, player):
        now = pygame.time.get_ticks()
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist > self.STOP_DISTANCE:
            step = self.speed
            self.x += step * dx / dist
            self.y += step * dy / dist

            maior = max(abs(dx), abs(dy))
            if maior > 0 and min(abs(dx), abs(dy)) / maior > 0.4:
                if   dx > 0 and dy < 0: self.direction = 'up_right'
                elif dx < 0 and dy < 0: self.direction = 'up_left'
                elif dx > 0 and dy > 0: self.direction = 'down_right'
                else:                   self.direction = 'down_left'
            elif abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'

            self.frame_timer += self.FRAME_SPEED
        else:
            self.frame_timer = 0

        if self.hit_flash > 0 and now >= self.hit_flash:
            self.hit_flash = 0

    def take_damage(self, damage, weapon_name=None):
        self.hits_taken += 1
        hits_to_die = self.HITS_TO_DIE_BY_WEAPON.get(weapon_name, self.HITS_TO_DIE_BY_WEAPON['Punhos'])
        self.health = max(0, hits_to_die - self.hits_taken)
        self.hit_flash = pygame.time.get_ticks() + 160
        return self.hits_taken >= hits_to_die


class Mago:
    def __init__(self, x, y, assets, side='left'):
        self.kind = 'mago'
        self.side = side
        self.x = float(x)
        self.y = float(y)

        self.health = 4
        self.max_health = 4
        self.hits_taken = 0
        self.hits_to_die_by_weapon = {
            'Punhos': 4,
            'Cajado': 2,
            'Espada': 1,
        }
        self.damage = 0
        self.coins_reward = random.randint(1, 3)
        self.hit_flash = 0

        img = assets['mago_left'] if side == 'left' else assets['mago_right']
        self.static_image = pygame.transform.smoothscale(
            img,
            (int(img.get_width() * 1.1), int(img.get_height() * 1.1))
        )

        self.last_cast_ms = 0
        self.cast_cooldown_ms = 2300

    def rect(self):
        return self.static_image.get_rect(center=(int(self.x), int(self.y)))

    def get_current_frame(self):
        return self.static_image

    def update(self, player):
        pass

    def take_damage(self, damage, weapon_name=None):
        self.hits_taken += 1
        hits_to_die = self.hits_to_die_by_weapon.get(weapon_name, self.hits_to_die_by_weapon['Punhos'])
        self.health = max(0, hits_to_die - self.hits_taken)
        self.hit_flash = pygame.time.get_ticks() + 120
        return self.hits_taken >= hits_to_die

    def can_cast(self):
        return pygame.time.get_ticks() - self.last_cast_ms >= self.cast_cooldown_ms

    def cast_spell(self, assets, arena_center_x, arena_center_y):
        self.last_cast_ms = pygame.time.get_ticks()

        start = pygame.Vector2(self.x, self.y)
        center = pygame.Vector2(arena_center_x, arena_center_y)

        # destino no lado oposto do círculo
        end = center * 2 - start

        frames = [
            assets['water_spell_1'],
            assets['water_spell_2'],
            assets['water_spell_3'],
            assets['water_spell_4'],
            assets['water_spell_5'],
        ]

        return MageSpell(self.x, self.y, end.x, end.y, frames, speed=10, damage=2)
    
class MagoEvo(Mago):
    def __init__(self, x, y, assets, side='left'):
        super().__init__(x, y, assets, side=side)
        self.kind = ENEMY_MAGO_EVO

        self.health = 7
        self.max_health = 7
        self.hits_to_die_by_weapon = {
            'Punhos': 6,
            'Cajado': 4,
            'Espada': 2,
        }
        self.coins_reward = random.randint(3, 6)
        self.cast_cooldown_ms = 1600

        img = assets['mago_evo_left'] if side == 'left' else assets['mago_evo_right']
        self.static_image = pygame.transform.smoothscale(
            img,
            (int(img.get_width() * 0.60), int(img.get_height() * 0.60))
        )

    def cast_spell(self, assets, arena_center_x, arena_center_y):
        self.last_cast_ms = pygame.time.get_ticks()
        start = pygame.Vector2(self.x, self.y)
        center = pygame.Vector2(arena_center_x, arena_center_y)
        end = center * 2 - start
        frames = [
            assets['fire_spell_1'],
            assets['fire_spell_2'],
            assets['fire_spell_3'],
            assets['fire_spell_4'],
            assets['fire_spell_5'],
        ]
        return MageSpell(self.x, self.y, end.x, end.y, frames, speed=13, damage=4, damage_divisor=1.5)


class EsqueletoSpace(Enemy):
    KIND = 'esqueleto_space_sheet'
    HP_RANGE = (3, 3)
    HITS_TO_DIE_BY_WEAPON = {'Punhos': 7, 'Cajado': 4, 'Espada': 3}
    DAMAGE = 6
    SPEED_RANGE = (5, 9)
    COINS_RANGE = (3, 6)
    ATTACK_RANGE = 130
    ATTACK_COOLDOWN_MS = 180
    ATTACK_DURATION_MS = 150

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)
        self.kind = 'esqueleto_space'


class LobisomemSpace(Enemy):
    KIND = 'lobisomem_space_sheet'
    HP_RANGE = (12, 12)
    HITS_TO_DIE_BY_WEAPON = {'Punhos': 14, 'Cajado': 8, 'Espada': 5}
    DAMAGE = 12
    SPEED_RANGE = (4, 7)
    COINS_RANGE = (5, 9)
    ATTACK_RANGE = 160
    ATTACK_COOLDOWN_MS = 900
    ATTACK_DURATION_MS = 450

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)
        self.kind = 'lobisomem_space'


class LeaoSpace(Enemy):
    KIND = 'leao_space_sheet'
    HP_RANGE = (18, 18)
    HITS_TO_DIE_BY_WEAPON = {'Punhos': 20, 'Cajado': 13, 'Espada': 9}
    DAMAGE = 16
    SPEED_RANGE = (4, 6)
    COINS_RANGE = (10, 18)
    SCALE = 1.8
    ATTACK_RANGE = 180
    ATTACK_COOLDOWN_MS = 1200
    ATTACK_DURATION_MS = 600

    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)
        self.kind = 'leao_space'


class MagoSpace(MagoEvo):
    def __init__(self, x, y, assets, side='left'):
        super().__init__(x, y, assets, side=side)
        self.kind = 'mago_space'
        self.health = 10
        self.max_health = 10
        self.hits_to_die_by_weapon = {'Punhos': 9, 'Cajado': 6, 'Espada': 3}
        self.coins_reward = random.randint(5, 9)
        self.cast_cooldown_ms = 1200
        img = assets['mago_space_left'] if side == 'left' else assets['mago_space_right']
        self.static_image = pygame.transform.smoothscale(
            img, (int(img.get_width() * 0.45), int(img.get_height() * 0.45))
        )

    def cast_spell(self, assets, arena_center_x, arena_center_y):
        self.last_cast_ms = pygame.time.get_ticks()
        start = pygame.Vector2(self.x, self.y)
        center = pygame.Vector2(arena_center_x, arena_center_y)
        end = center * 2 - start
        frames = [assets[f'space_spell_{i}'] for i in range(1, 6)]
        return MageSpell(self.x, self.y, end.x, end.y, frames, speed=15, damage=5, full_damage=True)


class WeaponPickup:
    def __init__(self, x, y, image, name, price):
        self.name = name
        self.price = price
        self.sheet = image

        frame = melhor_frame_visivel(self.sheet, grid=8)
        self.image = pygame.transform.smoothscale(frame, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))

        self.equip_sheet = self.sheet

    def draw(self, screen, cam_x, cam_y, show_hint=True):
        sx = self.rect.x - cam_x
        sy = self.rect.y - cam_y
        screen.blit(self.image, (sx, sy))

class MageSpell:
    def __init__(
        self,
        start_x,
        start_y,
        end_x,
        end_y,
        frames,
        speed=8,
        damage=2,
        full_damage=False,
        damage_divisor=2,
    ):
        self.pos = pygame.Vector2(start_x, start_y)
        self.start = pygame.Vector2(start_x, start_y)
        self.end = pygame.Vector2(end_x, end_y)

        self.frames = frames
        self.speed = speed
        self.damage = damage
        self.full_damage = full_damage
        self.damage_divisor = damage_divisor

        self.direction = self.end - self.start
        self.total_distance = self.direction.length()
        if self.total_distance == 0:
            self.total_distance = 1
        self.direction = self.direction.normalize()

        self.traveled = 0.0
        self.frame_index = 0
        self.alive = True

    def update(self, player):
        if not self.alive:
            return False

        self.pos += self.direction * self.speed
        self.traveled += self.speed

        progress = min(1.0, self.traveled / self.total_distance)
        self.frame_index = min(4, int(progress * 5))

        spell_rect = self.rect()
        player_rect = pygame.Rect(player.x - 18, player.y - 34, 36, 68)

        if spell_rect.colliderect(player_rect):
            damage = self.damage if self.full_damage else max(1, round(self.damage / self.damage_divisor))
            player.take_damage(damage)
            self.alive = False
            return True

        if self.traveled >= self.total_distance:
            self.alive = False

        return False

    def rect(self):
        img = self.frames[self.frame_index]
        return img.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, screen, cam_x, cam_y):
        if not self.alive:
            return
        img = self.frames[self.frame_index]
        r = self.rect()
        screen.blit(img, (r.x - cam_x, r.y - cam_y))


class Arrow:
    def __init__(self, x, y, target_x, target_y, image, speed=18, damage=1):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.damage = damage
        self.alive = True

        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed
        else:
            self.vx = float(speed)
            self.vy = 0.0

        angle = -math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(image, angle)

    def update(self, enemies, arena_cx, arena_cy, arena_radius=785):
        if not self.alive:
            return None, False

        self.x += self.vx
        self.y += self.vy

        if math.hypot(self.x - arena_cx, self.y - arena_cy) > arena_radius:
            self.alive = False
            return None, False

        arrow_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        for enemy in enemies:
            if arrow_rect.colliderect(enemy.rect()):
                died = enemy.take_damage(self.damage, 'Arco')
                self.alive = False
                return enemy, died

        return None, False

    def draw(self, screen, cam_x, cam_y):
        r = self.image.get_rect(center=(int(self.x) - cam_x, int(self.y) - cam_y))
        screen.blit(self.image, r)
