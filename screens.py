import pygame

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
TITLE_FONT = pygame.font.SysFont(None, 70)  # Väčší font pre nadpisy
BUTTON_FONT = pygame.font.SysFont(None, 40)  # Menší font pre tlačidlá
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def intro_screen():
    intro = True
    button_width, button_height = 250, 80
    start_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - 50, button_width, button_height)
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 50, button_width, button_height)

    while intro:
        screen.fill((0, 0, 0))
        title_text = TITLE_FONT.render("Teleported to the NIGHTMARE", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))

        title_text = TITLE_FONT.render("Vytvoril Adam Gál", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT - title_text.get_height() - 20))

        pygame.draw.rect(screen, (50, 50, 50), start_button, border_radius=10)
        pygame.draw.rect(screen, (50, 50, 50), quit_button, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), start_button, 3, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), quit_button, 3, border_radius=10)

        start_text = BUTTON_FONT.render("Spustiť hru", True, (200, 200, 200))
        quit_text = BUTTON_FONT.render("Ukončiť", True, (200, 200, 200))

        screen.blit(start_text, (start_button.x + (button_width - start_text.get_width()) // 2,
                                 start_button.y + (button_height - start_text.get_height()) // 2))
        screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2,
                                quit_button.y + (button_height - quit_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    intro = False
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    quit()


def pause_screen():
    paused = True
    button_width, button_height = 250, 80
    resume_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - 50, button_width, button_height)
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 50, button_width, button_height)

    while paused:
        screen.fill((0, 0, 0))
        pause_text = TITLE_FONT.render("Hra pozastavená", True, (255, 255, 0))
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 3))

        pygame.draw.rect(screen, (50, 50, 50), resume_button, border_radius=10)
        pygame.draw.rect(screen, (50, 50, 50), quit_button, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), resume_button, 3, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), quit_button, 3, border_radius=10)

        resume_text = BUTTON_FONT.render("Pokračovať", True, (200, 200, 200))
        quit_text = BUTTON_FONT.render("Ukončiť", True, (200, 200, 200))

        screen.blit(resume_text, (resume_button.x + (button_width - resume_text.get_width()) // 2,
                                  resume_button.y + (button_height - resume_text.get_height()) // 2))
        screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2,
                                quit_button.y + (button_height - quit_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    paused = False
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False


def game_over_screen():
    game_over = True
    button_width, button_height = 250, 80
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 50, button_width, button_height)

    while game_over:
        screen.fill((0, 0, 0))
        game_over_text = TITLE_FONT.render("Koniec hry!", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))

        game_over_text = TITLE_FONT.render("Vytvoril Adam Gál", True, (255, 255, 255))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT - game_over_text.get_height() - 20))

        pygame.draw.rect(screen, (50, 50, 50), quit_button, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), quit_button, 3, border_radius=10)

        quit_text = BUTTON_FONT.render("Ukončiť", True, (200, 200, 200))

        screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2,
                                quit_button.y + (button_height - quit_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and quit_button.collidepoint(event.pos):
                pygame.quit()
                quit()
