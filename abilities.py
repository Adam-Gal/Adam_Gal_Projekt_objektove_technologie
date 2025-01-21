import pygame
import os
import math


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, damage, max_distance=500):
        super().__init__()
        self.image = pygame.Surface((20, 20))  # Example projectile size
        self.image.fill((255, 0, 0))  # Fill with red color for visibility
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.max_distance = max_distance
        self.start_pos = (x, y)
        self.distance_traveled = 0

    def update(self, player=None):
        if player:
            # Calculate the direction towards the player
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            self.direction = math.atan2(dy, dx)  # Update the direction towards the player

        # Move the projectile in the calculated direction
        self.rect.x += math.cos(self.direction) * self.speed
        self.rect.y += math.sin(self.direction) * self.speed

        # Update distance traveled
        dx = self.rect.x - self.start_pos[0]
        dy = self.rect.y - self.start_pos[1]
        self.distance_traveled = math.sqrt(dx ** 2 + dy ** 2)

        # Remove the projectile if it exceeds the maximum distance
        if self.distance_traveled >= self.max_distance:
            self.kill()

    def check_collision_with_npcs(self, npc_group):
        """Check if the projectile hits any NPC."""
        for npc in npc_group:
            if self.rect.colliderect(npc.rect):
                npc.health -= self.damage
                if npc.health <= 0:
                    npc.kill()
                self.kill()


class AbilitySystem:
    def __init__(self):
        self.abilities = pygame.sprite.Group()
        self.selected_ability = "Fireball"
        self.last_ability_time = 0
        self.ability_cooldown = 500
        self.projectiles = pygame.sprite.Group()  # Keep track of projectiles

    def trigger_ability(self, x, y, direction, camera_x, camera_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_ability_time >= self.ability_cooldown:
            if self.selected_ability == "Fireball":
                # Adjust mouse position to world coordinates by subtracting the camera position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_x += camera_x
                mouse_y += camera_y

                # Calculate the angle toward the mouse from the player's position
                angle = math.atan2(mouse_y - y, mouse_x - x)

                # Create a projectile
                projectile = Projectile(x, y, angle, speed=10, damage=20)
                self.projectiles.add(projectile)
            self.last_ability_time = current_time

    def update_abilities(self, player=None):
        """Update all active abilities, including projectiles."""
        for projectile in self.projectiles:
            projectile.update(player)

    def draw_abilities(self, screen, camera_x, camera_y):
        """Draw all projectiles on the screen."""
        for projectile in self.projectiles:
            screen.blit(projectile.image, projectile.rect.move(-camera_x, -camera_y))
