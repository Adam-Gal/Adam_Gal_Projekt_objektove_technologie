import pygame
import math
from animation_loader import load_animation_frames  # Import the new animation loader function

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, camera_x, camera_y, direction, speed, damage, animation_path, effect=None, max_distance=300, offset=20):
        super().__init__()
        self.animation_frames = load_animation_frames(animation_path)  # Use the new function
        self.current_frame = 0
        self.animation_speed = 3
        self.animation_counter = 0
        self.camera_x = camera_x
        self.camera_y = camera_y

        self.hit_npc_sound = pygame.mixer.Sound("Assets/Sounds/Npc/ough.mp3")
        self.hit_npc_sound.set_volume(0.3)

        # Calculate offset from player
        self.offset = offset
        offset_x = math.cos(direction) * self.offset
        offset_y = math.sin(direction) * self.offset
        start_x = x + offset_x
        start_y = y + offset_y

        # Projectile image intialization
        self.direction = direction
        self.image = self.animation_frames[self.current_frame]
        self.image = pygame.transform.rotate(self.image, -math.degrees(self.direction))
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)

        # Other parameters for projectile
        self.speed = speed
        self.damage = damage
        self.effect = effect
        self.max_distance = max_distance
        self.start_pos = self.rect.center
        self.distance_traveled = 0

    def update(self, npc_group, floating_text_group):
        # Projectile movement
        self.rect.x += math.cos(self.direction) * self.speed
        self.rect.y += math.sin(self.direction) * self.speed

        # Distance calculation
        dx = self.rect.centerx - self.start_pos[0]
        dy = self.rect.centery - self.start_pos[1]
        self.distance_traveled = math.sqrt(dx ** 2 + dy ** 2)

        if self.distance_traveled >= self.max_distance:
            self.kill()

        # Animation update
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = pygame.transform.rotate(
                self.animation_frames[self.current_frame], -math.degrees(self.direction)
            )

        self.check_collision_with_npcs(npc_group, floating_text_group)

    def check_collision_with_npcs(self, npc_group, floating_text_group):
        for npc in npc_group:
            if self.rect.colliderect(npc.rect):
                self.hit_npc_sound.play()
                # Deal damage to NPC
                npc.take_damage(self.damage, floating_text_group)

                # Apply effect of projectile to the NPC
                if self.effect == "knockback":
                    npc.knockback(self.direction, 150)
                elif self.effect == "slow":
                    npc.apply_effect("slow", 3000)
                elif self.effect == "overheat":
                    npc.apply_effect("overheat", 3000)

                # Destroy projectile after collision
                self.kill()
                break


class EarthSpike(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, damage, lifetime=500, animation_path="Assets/Abilities/Earth"):
        super().__init__()
        self.radius = radius
        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime
        self.npc_group = []
        self.floating_text_group = []
        self.damage_applied = False

        # Animation load
        self.animation_frames = load_animation_frames(animation_path, 80, 80)  # Use the new function
        self.current_frame = 0
        self.animation_speed = lifetime // len(self.animation_frames)  # Trvanie každého snímku
        self.animation_timer = pygame.time.get_ticks()

        # First frame init
        self.image = pygame.transform.scale(self.animation_frames[self.current_frame], (radius * 2, radius * 2))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, npc_group, floating_text_group):
        current_time = pygame.time.get_ticks()
        self.npc_group = npc_group
        self.floating_text_group = floating_text_group

        # Play animation only once
        if current_time - self.animation_timer >= self.animation_speed and self.current_frame < len(self.animation_frames) - 1:
            self.current_frame += 1
            self.animation_timer = current_time
            self.image = pygame.transform.scale(self.animation_frames[self.current_frame], (self.radius * 2, self.radius * 2))
            self.rect = self.image.get_rect(center=self.rect.center)

        # Apply damage only once when the EarthSpike is created
        if not self.damage_applied:
            self.apply_damage()

        # Delete spikes
        if current_time - self.spawn_time > self.lifetime:
            self.kill()

    def apply_damage(self):
        # Apply damage to the NPC
        for npc in self.npc_group:
            distance = math.dist(self.rect.center, npc.rect.center)
            if distance <= self.radius:
                npc.take_damage(self.damage, self.floating_text_group)
                self.damage_applied = True

class AbilitySystem:
    def __init__(self, floating_text_group):
        self.projectiles = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()  # Skupina pre plávajúce texty
        self.selected_ability = "Fireball"
        self.last_ability_time = 0
        self.ability_cooldown = 500
        self.last_switch_time = 0
        self.switch_cooldown = 200
        self.abilities = ["Fireball", "Iceblast", "Wind", "Earthspikes"]
        self.floating_text_group = floating_text_group

        # Cooldown for abilities
        self.cooldowns = {
            "Fireball": {"cooldown": 500, "last_use": None},
            "Iceblast": {"cooldown": 500, "last_use": None},
            "Wind": {"cooldown": 500, "last_use": None},
            "Earthspikes": {"cooldown": 4000, "last_use": None},  # 7-sekundový cooldown
        }

        # Load sound effects
        self.fireball_sound = pygame.mixer.Sound("Assets/Sounds/Abilities/fireball.mp3")
        self.iceblast_sound = pygame.mixer.Sound("Assets/Sounds/Abilities/iceblast.mp3")
        self.wind_sound = pygame.mixer.Sound("Assets/Sounds/Abilities/wind.mp3")
        self.earthspikes_sound = pygame.mixer.Sound("Assets/Sounds/Abilities/earthspikes.mp3")
        self.choose_ability_click_sound = pygame.mixer.Sound("Assets/Sounds/UI/click.mp3")
        self.fireball_sound.set_volume(0.2)
        self.iceblast_sound.set_volume(0.2)
        self.wind_sound.set_volume(0.1)
        self.earthspikes_sound.set_volume(0.4)
        self.choose_ability_click_sound.set_volume(0.6)

    def switch_ability_forward(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_switch_time >= self.switch_cooldown:
            current_index = self.abilities.index(self.selected_ability)
            self.selected_ability = self.abilities[(current_index + 1) % len(self.abilities)]
            self.last_switch_time = current_time
            self.choose_ability_click_sound.play()

    def switch_ability_backward(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_switch_time >= self.switch_cooldown:
            current_index = self.abilities.index(self.selected_ability)
            self.selected_ability = self.abilities[(current_index - 1) % len(self.abilities)]
            self.last_switch_time = current_time
            self.choose_ability_click_sound.play()

    def select_ability_by_index(self, index):
        if 0 <= index < len(self.abilities):
            self.selected_ability = self.abilities[index]

    def trigger_ability(self, x, y, camera_x, camera_y):
        current_time = pygame.time.get_ticks()

        # Check cooldown
        ability_data = self.cooldowns[self.selected_ability]
        if ability_data["last_use"] is None or current_time - ability_data["last_use"] >= ability_data["cooldown"]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x += camera_x
            mouse_y += camera_y

            angle = math.atan2(mouse_y - y, mouse_x - x)

            # Create projectiles or EarthSpike
            if self.selected_ability == "Fireball":
                animation_path = "Assets/Abilities/Fire"
                projectile = Projectile(x, y, camera_x, camera_y, angle, 3, 15, animation_path, "overheat", 150)
                self.fireball_sound.play()
                self.projectiles.add(projectile)
            elif self.selected_ability == "Iceblast":
                animation_path = "Assets/Abilities/Water"
                projectile = Projectile(x, y, camera_x, camera_y, angle, 3, 10, animation_path, "slow", 350)
                self.iceblast_sound.play()
                self.projectiles.add(projectile)
            elif self.selected_ability == "Wind":
                animation_path = "Assets/Abilities/Wind"
                projectile = Projectile(x, y, camera_x, camera_y, angle, 8, 2, animation_path, "knockback", 500)
                self.wind_sound.play()
                self.projectiles.add(projectile)
            elif self.selected_ability == "Earthspikes":

                # Get mouse position
                spike_x = mouse_x
                spike_y = mouse_y

                # EarthSpike parameters
                radius = 40
                damage = 40
                lifetime = 1000
                animation_path = "Assets/Abilities/Earth"

                # Create and add
                spike = EarthSpike(spike_x, spike_y, radius, damage, lifetime, animation_path)
                self.spikes.add(spike)
                spike.apply_damage()
                self.earthspikes_sound.play()

            # Save last use time
            ability_data["last_use"] = current_time
            self.last_ability_time = current_time


    def update_abilities(self, npc_group):
        self.projectiles.update(npc_group, self.floating_text_group)
        self.spikes.update(npc_group, self.floating_text_group)
        self.floating_texts.update()

    def draw_abilities(self, screen, camera_x, camera_y):
        for projectile in self.projectiles:
            screen.blit(projectile.image, projectile.rect.move(-camera_x, -camera_y))
        for spike in self.spikes:
            screen.blit(spike.image, spike.rect.move(-camera_x, -camera_y))