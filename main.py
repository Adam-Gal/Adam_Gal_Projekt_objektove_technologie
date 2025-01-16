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
player_size = 50

# Initialize player
player = Player(player_size, player_size, "Assets/Player")
stamina_bar = StaminaBar(player)  # Create stamina bar for the player

# Initialize ability system
ability_system = AbilitySystem()

# Initialize the display for selected ability
selected_ability_display = SelectedAbilityDisplay(ability_system)

# Camera settings
camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)  # Camera position and size
camera_speed = 0.1  # Speed of camera smoothing
camera_offset = pygame.Vector2(0, 0)  # Optional camera offset

# Initially set the camera to be centered on the player
camera.center = player.rect.center

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

    # Handle ability selection and triggering
    if keys[pygame.K_q]:
        ability_system.cycle_ability("prev")  # Cycle to the previous ability
    if keys[pygame.K_e]:
        ability_system.cycle_ability("next")  # Cycle to the next ability
    # Handle abilities
    if keys[pygame.K_SPACE]:
        ability_system.trigger_ability(player.rect.centerx, player.rect.centery, player.facing_direction)

    # Update and draw abilities
    ability_system.update_abilities()
    ability_system.draw_abilities(screen, camera.x, camera.y)

    # Smooth camera movement (camera follows player with some smoothing and offset)
    target_camera_position = pygame.Vector2(player.rect.center) + camera_offset
    camera.centerx += (target_camera_position.x - camera.centerx) * camera_speed
    camera.centery += (target_camera_position.y - camera.centery) * camera_speed

    # Draw player (after adjusting the camera)
    screen.blit(player.image, player.rect.move(-camera.x, -camera.y))

    # Draw the player's hitbox (adjusted based on camera position)
    pygame.draw.rect(screen, (255, 0, 0), player.rect.move(-camera.x, -camera.y), 2)  # Red color with 2px border

    # Draw stamina bar (adjust position based on camera)
    stamina_bar.draw(screen, 20, 20, 200, 20)

    # Draw the selected ability (adjust position based on camera)
    selected_ability_display.draw(screen, 20, 50)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
