import pygame
import random
from config import *
from os import path
from assets_loader import *
from sprites import cortar_spritesheet





def game_screen(screen, assets):

    clock = pygame.time.Clock()

    background_arena = assets[ARENA_COLISEU]

    map_width = background_arena.get_width()
    map_height = background_arena.get_height()
    sheet = assets["player_sheet"]

    frame_w = sheet.get_width() // 8
    frame_h = sheet.get_height() // 8

    frames = cortar_spritesheet(sheet, frame_w, frame_h)
    print(sheet.get_width(), sheet.get_height())

    animacoes = {
        "down": frames[6],
        "left": frames[1],
        "right": frames[3],
        "up": frames[2]
    }

    player_x = background_arena.get_width() // 2
    player_y = background_arena.get_height() // 2

    direction = "down"
    frame_timer = 0
    speed = 5

    running = True
    state = GAME

    #Câmera começa no centro
    vcamerax = (map_width - LARGURA) // 2
    vcameray = (map_height - ALTURA) // 2


    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = QUIT
                running = False

        keys = pygame.key.get_pressed()

        dx, dy = 0, 0

        if keys[pygame.K_a]:
            dx -= speed
        if keys[pygame.K_d]:
            dx += speed
        if keys[pygame.K_w]:
            dy -= speed
        if keys[pygame.K_s]:
            dy += speed

        player_x += dx
        player_y += dy
        
        moving = (dx != 0 or dy != 0)

        if moving:
            if abs(dx) > abs(dy):
                direction = "right" if dx > 0 else "left"
            else:
                direction = "down" if dy > 0 else "up"

            frame_timer += 0.15
            if frame_timer >= len(animacoes[direction]):
                frame_timer = 0
        else:
            frame_timer = 0

        # atualiza a câmera
        vcamerax = player_x - LARGURA // 2
        vcameray = player_y - ALTURA // 2
        #Limitando Câmera, para não sair do mapa
        vcamerax = max(0, min(vcamerax, map_width - LARGURA))
        vcameray = max(0, min(vcameray, map_height - ALTURA))

        frame_index = int(frame_timer)
        player_frame = animacoes[direction][frame_index]
        screen.fill((0, 0, 0))
        screen.blit(background_arena, (-vcamerax, -vcameray))

        screen.blit(
            player_frame,
            (
                LARGURA // 2 - player_frame.get_width() // 2,
                ALTURA // 2 - player_frame.get_height() // 2
            )
        )

        pygame.display.flip()

    return state