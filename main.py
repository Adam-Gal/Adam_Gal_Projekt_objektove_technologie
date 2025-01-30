import pygame
import pytmx
import time
from pytmx.util_pygame import load_pygame
from npc import NPCManager
from player import Player
from abilities import AbilitySystem
from utils import get_spawn_position
from stats import StaminaBar, AbilityDisplay, HealthBar, TimerDisplay
import map
from camera import Camera

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
player_size = 50
camera_speed = 0.1
TIME_LIMIT = 150# Time limit in seconds
SWITCH_COOLDOWN = 200  # Cooldown time for ability switching
FONT = pygame.font.SysFont(None, 45)  # Font for timer display

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Map and player initialization
map_file = "LavaPlace.tmx"
tmx_data = load_pygame(map_file)
map_width, map_height = tmx_data.width * tmx_data.tilewidth, tmx_data.height * tmx_data.tileheight
spawn_x, spawn_y = get_spawn_position(tmx_data)
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
npc_manager = NPCManager(floating_text_group, tmx_data, 0, 50, 40, "Assets/Maps/LavaPlace/Npc/Demon", 50, 40, 5)
npc_spawned_once = False
spawn_npcs = False

# Ability system
ability_system = AbilitySystem(npc_manager.npcs, floating_text_group)
selected_ability_display = AbilityDisplay(ability_system)

# Main loop
clock = pygame.time.Clock()
start_time = time.time()
running = True
last_switch_time = 0

def load_new_map(new_map_file):
    global tmx_data, map_width, map_height, map_instance, npc_manager, camera

    # Načítanie novej mapy
    tmx_data = load_pygame(new_map_file)
    map_width, map_height = tmx_data.width * tmx_data.tilewidth, tmx_data.height * tmx_data.tileheight

    # Aktualizácia objektov závislých na mape
    map_instance = map.Map(tmx_data, TIME_LIMIT)
    if new_map_file == "AirPlace.tmx":
        npc_manager = NPCManager(floating_text_group, tmx_data, 0, 30, 40, "Assets/Maps/AirPlace/Npc/AirGolem", 85, 50, 8)
    elif new_map_file == "SnowPlace.tmx":
        npc_manager = NPCManager(floating_text_group, tmx_data, 0, 30, 40, "Assets/Maps/SnowPlace/Npc/IceGolem", 85, 60, 12)
    elif new_map_file == "DirtPlace.tmx":
        npc_manager = NPCManager(floating_text_group, tmx_data, 0, 30, 40, "Assets/Maps/DirtPlace/Npc/DirtGolem", 85, 70, 14)


    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, map_width, map_height, camera_speed)

    # Získanie novej pozície pre hráča
    spawn_x, spawn_y = get_spawn_position(tmx_data) or (50, 50)
    player.check_collision_with_objects(player.rect, tmx_data)
    player.rect.topleft = (spawn_x - 10, spawn_y - player_size / 2)
    player.bottom_half_rect.topleft = (spawn_x - 10, spawn_y - player_size / 2 + player_size // 2)

    # Po spawne novej mapy
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, map_width, map_height, camera_speed)
    camera.update(player.rect)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Posun kolieska hore
                ability_system.switch_ability_forward()
            elif event.y < 0:  # Posun kolieska dole
                ability_system.switch_ability_backward()

    screen.fill((0, 0, 0))

    if timer_display.start_timer is not None:
        elapsed_time = time.time() - timer_display.start_timer
        if elapsed_time >= timer_display.time_limit or map_instance.stopTimer:
            # Reset časovača
            timer_display.reset()

            # Reset kontrolného panela
            map_instance.controllPanelOn = False
            map_instance.reset_control_panel()
            map_instance.stopTimer = False

            # Despawn NPCs
            spawn_npcs = False
            npc_spawned_once = False
            npc_manager.despawn_all_npcs()

    # Kontrola teleportov
    if player.is_teleported():
        load_new_map(player.new_map)
        player.teleported = False
        player.new_map = ""

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
        ability_system.trigger_ability(player.rect.centerx, player.rect.centery, *camera.get_offset())

    # Update projectiles and check for collisions with NPCs
    ability_system.update_abilities()
    for projectile in ability_system.projectiles:
        projectile.check_collision_with_npcs(npc_manager.npcs, floating_text_group)

    # Prepínanie schopností pomocou číselných klávesov 1-4
    if keys[pygame.K_1]:
        ability_system.select_ability_by_index(0)
    elif keys[pygame.K_2]:
        ability_system.select_ability_by_index(1)
    elif keys[pygame.K_3]:
        ability_system.select_ability_by_index(2)
    elif keys[pygame.K_4]:
        ability_system.select_ability_by_index(3)

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
    stamina_bar.draw(screen, 20, SCREEN_HEIGHT - 40, 220, 25)
    health_bar.draw(screen, SCREEN_WIDTH-240, 20, 220, 25)
    selected_ability_display.draw(screen, 15, 15)
    timer_display.draw(screen, SCREEN_WIDTH/2, 20)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
