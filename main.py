import os
import pygame
from player import Player
from abilities import AbilitySystem
from stats import StaminaBar, SelectedAbilityDisplay

pygame.init()

# Screen settings
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize player
player = Player(50, 50, "Assets/Player")
stamina_bar = StaminaBar(player)  # Create stamina bar for the player

# Initialize ability system
ability_system = AbilitySystem()

# Initialize the display for selected ability
selected_ability_display = SelectedAbilityDisplay(ability_system)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 128, 255))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # Handle player movement and stamina
    player.handle_movement(keys)

    # Update stamina bar
    stamina_bar.update()

    # Handle abilities
    if keys[pygame.K_SPACE]:
        ability_system.trigger_ability(player.rect.centerx, player.rect.centery, player.facing_direction)

    # Handle ability selection and triggering
    if keys[pygame.K_q]:
        ability_system.cycle_ability("prev")  # Cycle to the previous ability
    if keys[pygame.K_e]:
        ability_system.cycle_ability("next")  # Cycle to the next ability
    if keys[pygame.K_SPACE]:
        ability_system.trigger_ability(player.rect.centerx, player.rect.centery, player.facing_direction)

    # Update and draw abilities
    ability_system.update_abilities()
    ability_system.draw_abilities(screen)

    # Draw player
    screen.blit(player.image, player.rect)

    # Draw stamina bar
    stamina_bar.draw(screen, 20, 20, 200, 20)

    # Draw the selected ability
    selected_ability_display.draw(screen, 20, 50)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
