import pygame
from os import path
from config import *
from ranking import sorted_ranking


def game_over(screen, assets):
    clock = pygame.time.Clock()

    background = screen.copy()
    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)

    defeat_font  = pygame.font.Font(path.join(FONT_DIR, 'HyliaSerifBeta-Regular.otf'), 96)
    ranking_font = pygame.font.Font(path.join(FONT_DIR, 'HyliaSerifBeta-Regular.otf'), 42)
    option_font  = pygame.font.Font(path.join(FONT_DIR, 'HyliaSerifBeta-Regular.otf'), 54)

    text      = defeat_font.render('Você perdeu', True, (255, 235, 220))
    text_rect = text.get_rect(center=(LARGURA_TELA // 2, 180))

    ranking_title      = ranking_font.render('RANKING', True, (255, 210, 100))
    ranking_title_rect = ranking_title.get_rect(center=(LARGURA_TELA // 2, 300))

    ranking_entries = sorted_ranking(limit=5)

    options_start_ms = pygame.time.get_ticks() + 5_000

    running = True

    while running:
        clock.tick(FPS)
        now          = pygame.time.get_ticks()
        show_options = now >= options_start_ms
        mouse_pos    = pygame.mouse.get_pos()

        play_again_text = option_font.render('Jogar novamente', True, (255, 235, 220))
        quit_text       = option_font.render('Sair', True, (255, 235, 220))
        play_again_rect = play_again_text.get_rect(center=(LARGURA_TELA // 2, 820))
        quit_rect       = quit_text.get_rect(center=(LARGURA_TELA // 2, 900))

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

        alpha = 135 + int(25 * abs(pygame.math.Vector2(1, 0).rotate(now * 0.08).y))
        overlay.fill((160, 0, 0, alpha))
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(text, text_rect)
        screen.blit(ranking_title, ranking_title_rect)

        for i, entry in enumerate(ranking_entries):
            cor  = (255, 215, 0) if i == 0 else (255, 235, 220)
            line = ranking_font.render(f'{i + 1}.  {entry["name"]:<18}  {entry["score"]}', True, cor)
            screen.blit(line, line.get_rect(center=(LARGURA_TELA // 2, 370 + i * 70)))

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
