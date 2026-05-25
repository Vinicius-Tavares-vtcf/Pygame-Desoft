# ===== Inicialização =====
import pygame
from config import *
from os import path
import cv2
from assets_loader import *


def init_screen(screen, assets, current_player_name=''):
    clock = pygame.time.Clock()

    fade = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
    fade.fill((0, 0, 0))
    alpha = 255

    video = cv2.VideoCapture(path.join(IMG_DIR, 'Video Inicial.mp4'))

    txt_titulo = assets[TXT_TITULO]
    txt_titulo_rect = txt_titulo.get_rect(topleft=(-60, 20))

    txt_batalhar = assets[TXT_BATALHAR]
    txt_batalhar_rect = txt_batalhar.get_rect(topleft=(20, 370))
    txt_hover_batalhar = assets[HOVER_BATALHAR]

    txt_sair = assets[TXT_SAIR]
    txt_sair_rect = txt_sair.get_rect(topleft=(30, 610))
    txt_hover_sair = assets[HOVER_SAIR]
    name_font = pygame.font.Font(path.join(FONT_DIR, 'HyliaSerifBeta-Regular.otf'), 44)
    helper_font = pygame.font.Font(path.join(FONT_DIR, 'HyliaSerifBeta-Regular.otf'), 28)
    player_name = current_player_name.strip()[:18]

    pygame.mixer.music.load(assets[MUSICA_INICIAL])
    pygame.mixer.music.set_volume(1.0) # tava 0.3
    pygame.mixer.music.play(-1)

    som_path = assets.get(VIDEO_INICIAL)
    som_video = None
    if som_path:
        som_video = pygame.mixer.Sound(som_path)
        som_video.set_volume(1.0) #0.6
        som_video.play(-1)

    running = True
    state = GAME

    while running:
        clock.tick(FPS / 2)

        if alpha > 0:
            alpha -= 5
            fade.set_alpha(alpha)
            screen.blit(fade, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        is_hover_bat = txt_batalhar_rect.collidepoint(mouse_pos)
        is_hover_sair = txt_sair_rect.collidepoint(mouse_pos)

        if is_hover_sair or is_hover_bat:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN and player_name.strip():
                    state = GAME
                    running = False
                elif len(player_name) < 18 and event.unicode and event.unicode.isprintable():
                    player_name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if txt_batalhar_rect.collidepoint(event.pos) and player_name.strip():
                    state = GAME
                    running = False
                elif txt_sair_rect.collidepoint(event.pos):
                    state = QUIT
                    running = False
            if event.type == pygame.QUIT:
                state = QUIT
                running = False

        ret, frame = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (1280, 720))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.transform.scale(
            pygame.surfarray.make_surface(frame.swapaxes(0, 1)),
            (LARGURA_TELA, ALTURA_TELA)
        )

        screen.blit(frame_surface, (0, 0))
        screen.blit(txt_titulo, txt_titulo_rect)
        screen.blit(txt_hover_batalhar if is_hover_bat else txt_batalhar, txt_batalhar_rect)
        screen.blit(txt_hover_sair if is_hover_sair else txt_sair, txt_sair_rect)
        name_label = helper_font.render('Nome do jogador', True, (255, 235, 220))
        name_text = name_font.render(
            player_name if player_name else 'Digite seu nome',
            True,
            (255, 255, 255) if player_name else (170, 170, 170)
        )
        name_box = pygame.Rect(LARGURA_TELA - 600, 390, 500, 82)
        pygame.draw.rect(screen, (0, 0, 0), name_box, border_radius=6)
        pygame.draw.rect(screen, (255, 235, 220), name_box, 2, border_radius=6)
        screen.blit(name_label, (name_box.x, name_box.y - 38))
        screen.blit(name_text, (name_box.x + 18, name_box.y + 16))
        screen.blit(fade, (0, 0))

        pygame.display.flip()

    if som_video:
        som_video.stop()
    pygame.mixer.music.stop()
    video.release()
    return state, (player_name.strip() or 'Jogador')

