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
from camera import Camera

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
player_size = 50
camera_speed = 0.1
TIME_LIMIT = 10  # Time limit in seconds
SWITCH_COOLDOWN = 200  # Cooldown time for ability switching
FONT = pygame.font.SysFont(None, 36)  # Font for timer display

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
timer_display = TimerDisplay(TIME_LIMIT)

# Camera initialization
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, map_width, map_height, camera_speed)

# Map initialization
map_instance = map.Map(tmx_data, TIME_LIMIT)
floating_text_group = pygame.sprite.Group()

# NPC management
npc_manager = NPCManager(floating_text_group, tmx_data, 0, 50)
npc_spawned_once = False
spawn_npcs = False

# Ability system
ability_system = AbilitySystem(npc_manager.npcs, floating_text_group)
selected_ability_display = SelectedAbilityDisplay(ability_system)

# Main loop
clock = pygame.time.Clock()
start_time = time.time()
running = True
last_switch_time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Handle key inputs and player actions
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False
    player.handle_movement(keys, tmx_data)
    stamina_bar.update()
    ability_system.update_abilities()

    # Handle mouse events for shooting the projectile
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        ability_system.trigger_ability(player.rect.centerx, player.rect.centery, player.facing_direction, *camera.get_offset())

    # Update projectiles and check for collisions with NPCs
    ability_system.update_abilities()
    for projectile in ability_system.projectiles:
        projectile.check_collision_with_npcs(npc_manager.npcs, floating_text_group)


    # Handle ability switching
    current_time = pygame.time.get_ticks()
    if keys[pygame.K_e] and current_time - last_switch_time > SWITCH_COOLDOWN:
        ability_system.switch_ability_forward()
        last_switch_time = current_time
    elif keys[pygame.K_q] and current_time - last_switch_time > SWITCH_COOLDOWN:
        ability_system.switch_ability_backward()
        last_switch_time = current_time

    # Control panel interaction
    if keys[pygame.K_f]:
        if map_instance.is_near_control_panel(player.rect) and not map_instance.controll_panel_on:
            map_instance.turn_on_buttons()
            map_instance.controll_panel_on = True
            map_instance.start_timer = time.time()
            timer_display.start()
            if not npc_spawned_once:  # Spawn NPC only once
                spawn_npcs = True
                npc_spawned_once = True

        elif map_instance.is_near_button(player.rect):
            map_instance.turn_off_button(player.rect)

    if map_instance.despawn_npcs:
        spawn_npcs = False
        npc_spawned_once = False
        npc_manager.despawn_all_npcs()

    # Update camera and render everything
    camera.update(player.rect)
    map_instance.render_map_tiles(screen, tmx_data, camera.camera, start_time)
    map_instance.render_map_objects(screen, tmx_data, player, camera.camera, start_time)

    # Draw projectiles
    ability_system.draw_abilities(screen, *camera.get_offset())

    # Update and draw NPCs
    if spawn_npcs:
        npc_manager.update(player, camera.camera.x, camera.camera.y)
        npc_manager.draw(screen, camera.camera)

    # Player collision detection
    player.check_collision_with_objects(player.rect, tmx_data)

    # Update and draw floating texts
    floating_text_group.update(camera.camera.x, camera.camera.y)
    floating_text_group.draw(screen)

    # Draw UI elements
    stamina_bar.draw(screen, 20, 20, 200, 20)
    health_bar.draw(screen, 20, 50, 200, 20)
    selected_ability_display.draw(screen, 20, 50)
    timer_display.draw(screen, FONT, 10, 100)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
