import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from player import Player
from abilities import AbilitySystem
from stats import StaminaBar, SelectedAbilityDisplay

pygame.init()

# Screen settings
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
player_size = 50

# Load the map
map_file = "mapa.tmx"  # Path to your Tiled map
tmx_data = load_pygame(map_file)
map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight

# Initialize player
player = Player(player_size, player_size, "Assets/Player", 1000, 1000)
stamina_bar = StaminaBar(player)  # Create stamina bar for the player

# Initialize ability system
ability_system = AbilitySystem()

# Initialize the display for selected ability
selected_ability_display = SelectedAbilityDisplay(ability_system)

# Camera settings
camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)  # Camera position and size
camera_speed = 0.1  # Speed of camera smoothing

# Initially set the camera to be centered on the player
camera.center = player.rect.center

clock = pygame.time.Clock()
running = True


def render_map():
    """Render visible tiles of the map based on the camera position."""
    tile_width = tmx_data.tilewidth
    tile_height = tmx_data.tileheight

    # Calculate visible tile range
    start_x = max(0, camera.left // tile_width)
    end_x = min(tmx_data.width, (camera.right // tile_width) + 1)
    start_y = max(0, camera.top // tile_height)
    end_y = min(tmx_data.height, (camera.bottom // tile_height) + 1)

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if start_x <= x < end_x and start_y <= y < end_y:
                    tile_surface = tmx_data.get_tile_image_by_gid(gid)
                    if tile_surface:
                        # Calculate tile position relative to camera
                        x_pos = x * tile_width - camera.x
                        y_pos = y * tile_height - camera.y
                        screen.blit(tile_surface, (x_pos, y_pos))


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
    if keys[pygame.K_SPACE]:
        ability_system.trigger_ability(player.rect.centerx, player.rect.centery, player.facing_direction)

    # Update and draw abilities
    ability_system.update_abilities()

    # **Update the camera to center on the player**
    target_camera_position = pygame.Vector2(
        player.rect.centerx - SCREEN_WIDTH // 2,
        player.rect.centery - SCREEN_HEIGHT // 2
    )

    # Smoothly interpolate the camera's position toward the target
    camera.x += (target_camera_position.x - camera.x) * camera_speed
    camera.y += (target_camera_position.y - camera.y) * camera_speed

    # Ensure the camera stays within the bounds of the map
    camera.left = max(0, camera.left)
    camera.top = max(0, camera.top)
    camera.right = min(map_width, camera.right)
    camera.bottom = min(map_height, camera.bottom)

    # Draw the map (optimized rendering)
    render_map()

    # Draw player (after adjusting the camera)
    screen.blit(player.image, player.rect.move(-camera.x, -camera.y))

    # Draw the player's hitbox (adjusted based on camera position)
    pygame.draw.rect(screen, (255, 0, 0), player.rect.move(-camera.x, -camera.y), 2)  # Red color with 2px border

    # Draw abilities (make sure they appear after player)
    ability_system.draw_abilities(screen, camera.x, camera.y)

    # Draw stamina bar
    stamina_bar.draw(screen, 20, 20, 200, 20)

    # Draw the selected ability
    selected_ability_display.draw(screen, 20, 50)

    pygame.display.flip()
    clock.tick(120)  # Cap the framerate to 60 FPS

pygame.quit()
