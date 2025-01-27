# abilities.py
import pygame
import os
import math
from animation_loader import load_animation_frames  # Import the new animation loader function

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, camera_x, camera_y, direction, speed, damage, animation_path, effect=None, max_distance=300, offset=15):
        super().__init__()
        # Načítanie animácie pre projektil
        self.animation_frames = load_animation_frames(animation_path)  # Use the new function
        self.current_frame = 0
        self.animation_speed = 3
        self.animation_counter = 0
        self.camera_x = camera_x
        self.camera_y = camera_y

        # Vypočítať počiatočnú pozíciu na kružnici okolo hráča
        self.offset = offset
        offset_x = math.cos(direction) * self.offset
        offset_y = math.sin(direction) * self.offset
        start_x = x + offset_x
        start_y = y + offset_y

        # Nastavenie pozície a obrázka projektilu
        self.direction = direction
        self.image = self.animation_frames[self.current_frame]
        self.image = pygame.transform.rotate(self.image, -math.degrees(self.direction))
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)

        self.speed = speed
        self.damage = damage
        self.effect = effect
        self.max_distance = max_distance
        self.start_pos = self.rect.center
        self.distance_traveled = 0

    def update(self, npc_group=None, floating_text_group=None):
        # Pohyb projektilu
        self.rect.x += math.cos(self.direction) * self.speed
        self.rect.y += math.sin(self.direction) * self.speed

        # Výpočet vzdialenosti
        dx = self.rect.centerx - self.start_pos[0]
        dy = self.rect.centery - self.start_pos[1]
        self.distance_traveled = math.sqrt(dx ** 2 + dy ** 2)

        if self.distance_traveled >= self.max_distance:
            self.kill()

        # Aktualizácia animácie
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = pygame.transform.rotate(
                self.animation_frames[self.current_frame], -math.degrees(self.direction)
            )

        # Kontrola kolízie s NPC
        if npc_group and floating_text_group:
            self.check_collision_with_npcs(npc_group, floating_text_group)

    def check_collision_with_npcs(self, npc_group, floating_text_group):
        for npc in npc_group:
            if self.rect.colliderect(npc.rect):
                # Deal damage to NPC immediately
                npc.take_damage(self.damage, floating_text_group)

                if self.effect == "knockback":
                    npc.knockback(self.direction, 150)

                elif self.effect == "slow":
                    npc.apply_effect("slow", 3000)  # Apply slow for 3 seconds

                elif self.effect == "overheat":
                    npc.apply_effect("overheat", 3000)  # Apply overheat for 3 seconds

                # Destroy projectile after collision
                self.kill()
                break


class EarthSpike(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, damage, lifetime=500, animation_path="Assets/Abilities/Earth"):
        super().__init__()
        self.radius = radius  # Polomer EarthSpike
        self.damage = damage  # Poškodenie spôsobené NPC
        self.spawn_time = pygame.time.get_ticks()  # Čas vzniku
        self.lifetime = lifetime  # Celková životnosť (ms)
        self.npc_group = []  # Hold npc group passed at runtime
        self.floating_text_group = []  # Hold floating text group passed at runtime
        self.damage_applied = False  # Flag to ensure damage is applied only once

        # Načítanie animácie
        self.animation_frames = load_animation_frames(animation_path, 80, 80)  # Use the new function
        self.current_frame = 0
        self.animation_speed = lifetime // len(self.animation_frames)  # Trvanie každého snímku
        self.animation_timer = pygame.time.get_ticks()

        # Nastavenie prvého obrázka a pozície
        self.image = pygame.transform.scale(self.animation_frames[self.current_frame], (radius * 2, radius * 2))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, npc_group, floating_text_group):
        """Aktualizácia animácie, poškodenie NPC a kontrola životnosti."""
        current_time = pygame.time.get_ticks()
        self.npc_group = npc_group
        self.floating_text_group = floating_text_group

        # Aktualizácia animácie (prehrať iba raz počas lifetime)
        if current_time - self.animation_timer >= self.animation_speed and self.current_frame < len(self.animation_frames) - 1:
            self.current_frame += 1
            self.animation_timer = current_time
            self.image = pygame.transform.scale(self.animation_frames[self.current_frame], (self.radius * 2, self.radius * 2))
            self.rect = self.image.get_rect(center=self.rect.center)

        # Apply damage only once when the EarthSpike is created
        if not self.damage_applied:
            self.apply_damage()

        # Odstránenie EarthSpike po uplynutí životnosti
        if current_time - self.spawn_time > self.lifetime:
            self.kill()

    def apply_damage(self):
        """Aplikácia poškodenia NPC v dosahu (iba raz pri vzniku EarthSpike)."""
        for npc in self.npc_group:
            distance = math.dist(self.rect.center, npc.rect.center)
            if distance <= self.radius:
                npc.take_damage(self.damage, self.floating_text_group)
                self.damage_applied = True  # Mark that damage has been applied


class AbilitySystem:
    def __init__(self, npc_group, floating_text_group):
        self.projectiles = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()  # Skupina pre plávajúce texty
        self.selected_ability = "Fireball"
        self.last_ability_time = 0
        self.ability_cooldown = 500
        self.last_switch_time = 0
        self.switch_cooldown = 200
        self.abilities = ["Fireball", "Iceblast", "Wind", "Earth"]
        self.npc_group = npc_group
        self.floating_text_group = floating_text_group

        # Cooldowny pre jednotlivé schopnosti
        self.cooldowns = {
            "Fireball": {"cooldown": 500, "last_use": None},
            "Iceblast": {"cooldown": 500, "last_use": None},
            "Wind": {"cooldown": 500, "last_use": None},
            "Earth": {"cooldown": 7000, "last_use": None},  # 7-sekundový cooldown
        }

    def switch_ability_forward(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_switch_time >= self.switch_cooldown:
            current_index = self.abilities.index(self.selected_ability)
            self.selected_ability = self.abilities[(current_index + 1) % len(self.abilities)]
            self.last_switch_time = current_time

    def switch_ability_backward(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_switch_time >= self.switch_cooldown:
            current_index = self.abilities.index(self.selected_ability)
            self.selected_ability = self.abilities[(current_index - 1) % len(self.abilities)]
            self.last_switch_time = current_time

    def trigger_ability(self, x, y, direction, camera_x, camera_y):
        current_time = pygame.time.get_ticks()

        # Over cooldown pre aktuálne vybranú schopnosť
        ability_data = self.cooldowns[self.selected_ability]
        if ability_data["last_use"] is None or current_time - ability_data["last_use"] >= ability_data["cooldown"]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x += camera_x
            mouse_y += camera_y

            angle = math.atan2(mouse_y - y, mouse_x - x)

            if self.selected_ability == "Fireball":
                animation_path = "Assets/Abilities/Fire"
                projectile = Projectile(x, y, camera_x, camera_y, angle, 4, 15, animation_path, "overheat", 150)
                self.projectiles.add(projectile)

            elif self.selected_ability == "Iceblast":
                animation_path = "Assets/Abilities/Water"
                projectile = Projectile(x, y, camera_x, camera_y, angle, 3, 10, animation_path, "slow", 350)
                self.projectiles.add(projectile)

            elif self.selected_ability == "Wind":
                animation_path = "Assets/Abilities/Wind"
                projectile = Projectile(x, y, camera_x, camera_y, angle, 8, 2, animation_path, "knockback", 500)
                self.projectiles.add(projectile)


            elif self.selected_ability == "Earth":

                # Získaj pozíciu myši (už posunutú kamerou)
                spike_x = mouse_x
                spike_y = mouse_y

                # Parametre EarthSpike
                radius = 40
                damage = 40
                lifetime = 1000
                animation_path = "Assets/Abilities/Earth"

                # Vytvor a pridaj EarthSpike
                spike = EarthSpike(spike_x, spike_y, radius, damage, lifetime, animation_path)
                self.spikes.add(spike)
                spike.apply_damage()

            # Uloženie času posledného použitia
            ability_data["last_use"] = current_time
            self.last_ability_time = current_time


    def update_abilities(self):
        self.projectiles.update()
        self.spikes.update(self.npc_group, self.floating_text_group)
        self.floating_texts.update()

    def draw_abilities(self, screen, camera_x, camera_y):
        for projectile in self.projectiles:
            screen.blit(projectile.image, projectile.rect.move(-camera_x, -camera_y))
        for spike in self.spikes:
            screen.blit(spike.image, spike.rect.move(-camera_x, -camera_y))
