import pygame
import pytmx
import time
from pytmx.util_pygame import load_pygame
from player import Player
from abilities import AbilitySystem
from utils import get_tile_under_player, get_tile_properties, get_spawn_position
from stats import StaminaBar, SelectedAbilityDisplay, HealthBar

pygame.init()

# Initialize a clock to track the time for animations
start_time = time.time()

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
# Nájdite pozíciu pre spawn
spawn_position = get_spawn_position(tmx_data, 1)
if spawn_position:
    spawn_x, spawn_y = spawn_position
    player = Player(player_size, player_size, "Assets/Player", spawn_x-10, spawn_y-player_size/2)
else:
    player = Player(player_size, player_size, "Assets/Player", 1000, 1000)

stamina_bar = StaminaBar(player)  # Create stamina bar for the player
health_bar = HealthBar(player)

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
    tile_width, tile_height = tmx_data.tilewidth, tmx_data.tileheight

    # Calculate visible tile range
    start_x = max(0, camera.left // tile_width)
    end_x = min(tmx_data.width, (camera.right // tile_width) + 1)
    start_y = max(0, camera.top // tile_height)
    end_y = min(tmx_data.height, (camera.bottom // tile_height) + 1)

    # Get elapsed time for animations (in milliseconds)
    elapsed_time = (time.time() - start_time) * 1000

    # Iterate through visible layers
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if start_x <= x < end_x and start_y <= y < end_y and gid != 0:
                    # Get tile properties
                    tile_properties = tmx_data.get_tile_properties_by_gid(gid)

                    # If the tile has animation frames, handle the animation
                    if tile_properties and "frames" in tile_properties:
                        animation_frames = tile_properties["frames"]
                        if animation_frames:
                            total_duration = sum(duration for _, duration in animation_frames)
                            if total_duration > 0:
                                current_time = elapsed_time % total_duration
                            frame_duration_sum = 0

                            # Loop through the frames and select the one to display
                            for tileid, duration in animation_frames:
                                frame_duration_sum += duration
                                if current_time < frame_duration_sum:
                                    gid = tileid
                                    break

                    # Get the tile image for the current gid
                    tile_image = tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        # Draw tile at camera-adjusted position
                        x_pos = x * tile_width - camera.x
                        y_pos = y * tile_height - camera.y
                        screen.blit(tile_image, (x_pos, y_pos))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # Handle player movement and stamina
    player.handle_movement(keys, tmx_data)

    # Update stamina bar
    stamina_bar.update()

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

    # Handle ability selection and triggering
    if keys[pygame.K_q]:
        ability_system.cycle_ability("prev")  # Cycle to the previous ability
    if keys[pygame.K_e]:
        ability_system.cycle_ability("next")  # Cycle to the next ability
    if keys[pygame.K_SPACE]:
        ability_system.trigger_ability(player.rect.x+player_size/2, player.rect.y+player_size/2, player.facing_direction)

    # Draw the map (optimized rendering)
    render_map()

    # Get tile under player
    tile_x, tile_y = get_tile_under_player(player.rect, tmx_data)
    tile_properties = get_tile_properties(tile_x, tile_y, tmx_data)

    # Draw player (after adjusting the camera)
    screen.blit(player.image, player.rect.move(-camera.x, -camera.y))

    # Draw the player's hitbox (adjusted based on camera position)
    #pygame.draw.rect(screen, (255, 0, 0), player.rect.move(-camera.x, -camera.y), 2)  # Red color with 2px border

    # Draw abilities (make sure they appear after player)
    ability_system.draw_abilities(screen, camera.x, camera.y)

    # Draw stamina bar
    stamina_bar.draw(screen, 20, 20, 200, 20)
    health_bar.draw(screen, 20, 50, 200, 20)

    # Draw the selected ability
    selected_ability_display.draw(screen, 20, 50)

    pygame.display.flip()
    clock.tick(120)  # Cap the framerate to 60 FPS

pygame.quit()
