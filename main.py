# main.py
import pygame
import pytmx
import time
from pytmx.util_pygame import load_pygame

from npc import NPCManager
from player import Player
from abilities import AbilitySystem
from utils import get_spawn_position
from stats import StaminaBar, SelectedAbilityDisplay, HealthBar, TimerDisplay
import map

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
player_size = 50
camera_speed = 0.1

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Map and player initialization
map_file = "mapa.tmx"
tmx_data = load_pygame(map_file)
map_width, map_height = tmx_data.width * tmx_data.tilewidth, tmx_data.height * tmx_data.tileheight
spawn_x, spawn_y = get_spawn_position(tmx_data) or (1000, 1000)
player = Player(player_size, player_size, "Assets/Player", spawn_x - 10, spawn_y - player_size / 2)

# UI elements
stamina_bar = StaminaBar(player)
health_bar = HealthBar(player)
ability_system = AbilitySystem()
selected_ability_display = SelectedAbilityDisplay(ability_system)

# Camera initialization
camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
camera.center = player.rect.center

time_limit = 10  # Časový limit v sekundách
clock = pygame.time.Clock()
running = True
start_time = time.time()
timer_display = TimerDisplay(time_limit)  # Nastavte limit času (v sekundách)
font = pygame.font.SysFont(None, 36)  # Font pre zobrazenie časovača

# Initialize the Map
mapa = map.Map(tmx_data, time_limit)

npc_manager = NPCManager(tmx_data, 0, 50)
spawn_npcs = False

def update_camera():
    """Update camera position to center on player."""
    target_pos = pygame.Vector2(player.rect.centerx - SCREEN_WIDTH // 2, player.rect.centery - SCREEN_HEIGHT // 2)
    camera.x += (target_pos.x - camera.x) * camera_speed
    camera.y += (target_pos.y - camera.y) * camera_speed
    camera.left, camera.top = max(0, camera.left), max(0, camera.top)
    camera.right, camera.bottom = min(map_width, camera.right), min(map_height, camera.bottom)

# Main loop modification to handle the 'F' key press near a control panel
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Handle key inputs and player actions
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]: running = False
    player.handle_movement(keys, tmx_data)
    stamina_bar.update()
    ability_system.update_abilities()

    # Handle mouse events for shooting the projectile
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        # Trigger the ability (shoot a projectile)
        ability_system.trigger_ability(player.rect.centerx, player.rect.centery, player.facing_direction, camera.x, camera.y)

    # Update projectiles and check for collisions with NPCs
    ability_system.update_abilities()
    for projectile in ability_system.projectiles:
        projectile.check_collision_with_npcs(npc_manager.npcs)

    # Draw projectiles
    ability_system.draw_abilities(screen, camera.x, camera.y)

    npc_spawned_once = False

    if keys[pygame.K_f]:
        if mapa.is_near_control_panel(player.rect) and not mapa.controll_panel_on:
            mapa.turn_on_buttons()
            mapa.controll_panel_on = True
            mapa.start_timer = time.time()
            timer_display.start()
            if not npc_spawned_once:  # Spawn NPC iba raz
                spawn_npcs = True
                npc_spawned_once = True

        elif mapa.is_near_button(player.rect):
            mapa.turn_off_button(player.rect)

    if mapa.despawn_npcs:
        spawn_npcs = False
        npc_spawned_once = False
        npc_manager.despawn_all_npcs()



    # Update camera and render everything
    update_camera()
    mapa.render_map_tiles(screen, tmx_data, camera, start_time)
    mapa.render_map_objects(screen, tmx_data, player, camera, start_time)

    # V časti, kde spracovávate NPC
    if spawn_npcs:
        npc_manager.update(player, camera)
        npc_manager.draw(screen, camera)

    # Player collision detection
    player.check_collision_with_objects(player.rect, tmx_data)

    # UI elements
    stamina_bar.draw(screen, 20, 20, 200, 20)
    health_bar.draw(screen, 20, 50, 200, 20)
    selected_ability_display.draw(screen, 20, 50)
    timer_display.draw(screen, font, 10, 100)
    ability_system.draw_abilities(screen, camera.x, camera.y)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
