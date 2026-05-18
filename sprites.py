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

        scale_factor = 1.10 

        self.animacoes = {
            'down': _scale_frames(frames[6][:4], scale_factor),
            'left': _scale_frames(frames[1][:4], scale_factor),
            'right': _scale_frames(frames[3][:4], scale_factor),
            'up': _scale_frames(frames[2][:4], scale_factor),
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
    def equip(self, weapon_name, weapon_sheet=None):
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

        if weapon_sheet is not None:
            # pega uma parte visível da arma para desenhar na mão
            self.weapon_image = melhor_frame_visivel(weapon_sheet, grid=8)
        else:
            self.weapon_image = None

    def can_attack(self): # Verifica se já passou tempo suficiente para atacar de novo.
        return pygame.time.get_ticks() - self.last_attack_ms >= self.attack_cooldown_ms

    def start_attack(self): #Inicia o ataque e marca a direção do golpe.
        now = pygame.time.get_ticks()
        if not self.can_attack():
            return False
        self.last_attack_ms = now
        self.attack_start_ms = now
        self.attacking = True
        self.attack_direction = self.direction
        self.update_attack_box()
        return True

    def update_attack_box(self): #Cria a área de ataque na frente do personagem, dependendo da direção.
        box_size = self.attack_range
        if self.attack_direction == 'up':
            self.attack_box = pygame.Rect(self.x - box_size // 2, self.y - box_size, box_size, box_size)
        elif self.attack_direction == 'down':
            self.attack_box = pygame.Rect(self.x - box_size // 2, self.y + 10, box_size, box_size)
        elif self.attack_direction == 'left':
            self.attack_box = pygame.Rect(self.x - box_size, self.y - box_size // 2, box_size, box_size)
        else:
            self.attack_box = pygame.Rect(self.x + 10, self.y - box_size // 2, box_size, box_size)

    def update(self): #Atualiza o movimento, a direção, a animação e o ataque.
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

    def get_current_frame(self): #Retorna o frame certo da animação no momento atual.
        frames = self.attack_frames[self.attack_direction] if self.attacking else self.animacoes[self.direction]
        frame_index = int(self.frame_timer) % len(frames)
        return frames[frame_index]


class EnemyBase:
    KIND = ENEMY_ESQUELETO
    SPEED_RANGE = (2, 4)
    HP_RANGE = (2, 4)
    DAMAGE = 10
    COINS_RANGE = (1, 3)
    SCALE = 1.1
    FRAME_SPEED = 0.12

    def __init__(self, x, y, assets):
        self.kind = self.KIND
        self.sheet = assets[self.KIND]

        frame_w = self.sheet.get_width() // 8
        frame_h = self.sheet.get_height() // 8
        frames = cortar_spritesheet(self.sheet, frame_w, frame_h)

        self.animacoes = {
            'down': _scale_frames(frames[6][:4], self.SCALE),
            'left': _scale_frames(frames[1][:4], self.SCALE),
            'right': _scale_frames(frames[3][:4], self.SCALE),
            'up': _scale_frames(frames[2][:4], self.SCALE),
        }

        self.direction = 'down'
        self.frame_timer = 0
        self.x = float(x)
        self.y = float(y)
        self.speed = random.randint(*self.SPEED_RANGE)
        self.max_health = random.randint(*self.HP_RANGE)
        self.health = self.max_health
        self.damage = self.DAMAGE
        self.coins_reward = random.randint(*self.COINS_RANGE)
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

            self.frame_timer += self.FRAME_SPEED

        if self.hit_flash > 0 and now >= self.hit_flash:
            self.hit_flash = 0

    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = pygame.time.get_ticks() + 120
        return self.health <= 0


class Esqueleto(EnemyBase):
    KIND = ENEMY_ESQUELETO


class Lobisomem(EnemyBase):
    KIND = ENEMY_LOBISOMEM


class Mago(EnemyBase):
    KIND = ENEMY_MAGO

class WeaponPickup:
    def __init__(self, x, y, image, name):
        self.name = name
        self.sheet = image

        frame = melhor_frame_visivel(self.sheet, grid=8)

        self.image = pygame.transform.smoothscale(frame, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))

        self.equip_sheet = self.sheet

    def draw(self, screen, cam_x, cam_y):
        sx = self.rect.x - cam_x
        sy = self.rect.y - cam_y
        screen.blit(self.image, (sx, sy))
