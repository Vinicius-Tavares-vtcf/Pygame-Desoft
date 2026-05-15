import pygame
import random
from config import *
from os import path
from assets_loader import *
from sprites import *





def game_screen(screen, assets):

    clock = pygame.time.Clock()

    background_arena = assets[ARENA_COLISEU]

    map_width = background_arena.get_width()
    map_height = background_arena.get_height()
    player = Player(map_width,map_height,assets)

    frame_timer = player.frame_timer
    speed = player.speed
    
    running = True
    state = GAME

    #Câmera começa no centro
    vcamerax = (map_width - LARGURA_TELA) // 2
    vcameray = (map_height - ALTURA_TELA) // 2

    while running:
        clock.tick(FPS)
        andar = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = QUIT
                running = False

        keys = pygame.key.get_pressed()

        player.dx, player.dy = 0, 0

        if keys[pygame.K_a]:
            player.dx -= speed
        if keys[pygame.K_d]:
            player.dx += speed          
        if keys[pygame.K_w]:
            player.dy -= speed
        if keys[pygame.K_s]:
            player.dy += speed

        player.update()

        # atualiza a câmera
        vcamerax = player.x - LARGURA_TELA // 2
        vcameray = player.y - ALTURA_TELA // 2
        #Limitando Câmera, para não sair do mapa
        
        
        # vcamerax = max(0, min(vcamerax, map_width - LARGURA))
        # vcameray = max(0, min(vcameray, map_height - ALTURA))

        frame_index = int(player.frame_timer)
        player_frame = player.animacoes[player.direction][frame_index]
        largura_boneco = player_frame.get_width()
        altura_boneco = player_frame.get_height()

        player_frame = pygame.transform.smoothscale(player_frame,(largura_boneco*1.25,altura_boneco*1.25))
        screen.fill((0, 0, 0))
        screen.blit(background_arena, (-vcamerax, -vcameray))

        screen.blit(
            player_frame,
            (
                LARGURA_TELA // 2 - player_frame.get_width() // 2,
                ALTURA_TELA // 2 - player_frame.get_height() // 2
            )
        )
        
        pygame.display.flip()

    return state