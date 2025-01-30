import math
import os
import pygame
import random
import pytmx
import time
from utils import get_tile_under_player, get_walk_tile_properties
from animation_loader import load_animations


class NPC(pygame.sprite.Sprite):
    def __init__(self, floating_text_group, tmx_data, width, height, asset_path, start_x, start_y, attack_cooldown, max_approach_distance, max_detection_distance, hp, damage):
        super().__init__()
        self.frame_count = 0
        self.asset_path = asset_path
        self.width = width
        self.height = height
        self.rect = pygame.Rect(start_x, start_y, width, height)
        self.floating_text_group = floating_text_group
        self.camera_x = 0
        self.camera_y = 0

        # Animation setup
        self.animations = load_animations(asset_path, width, height)
        self.current_animation = "Idle"  # Default animation

        self.heart_image = pygame.image.load("Assets/Items/heart.png")  # Obrázok srdca
        self.heart_image = pygame.transform.scale(self.heart_image, (32, 32))

        # Check if animation exists and is valid
        if self.current_animation in self.animations and len(self.animations[self.current_animation]) > 0:
            self.image = self.animations[self.current_animation][0]
        else:
            raise ValueError(f"No valid frames found for animation '{self.current_animation}' in path '{asset_path}'.")

        self.animation_index = 0
        self.animation_speed = 0.1  # Frames per update
        self.last_frame_time = pygame.time.get_ticks()

        # Other attributes
        self.speed = 2.5
        self.attack_range = 40
        self.health = hp
        self.damage = damage
        self.attack_cooldown = attack_cooldown
        self.last_attack_time = 0
        self.max_approach_distance = max_approach_distance
        self.max_detection_distance = max_detection_distance
        self.tmx_data = tmx_data
        self.effects = {}
        self.knockback_target_pos = None
        self.knockback_speed = 10

    def load_animations(self, base_path):
        """Load animations from the specified base path."""
        animations = {}
        for animation_type in ["Attack", "Idle", "Walk"]:
            animation_path = os.path.join(base_path, animation_type)
            if os.path.exists(animation_path):
                frames = []
                for filename in sorted(os.listdir(animation_path), key=lambda x: int(x.split('.')[0])):
                    frame_path = os.path.join(animation_path, filename)
                    frame = pygame.image.load(frame_path)
                    frame = pygame.transform.scale(frame, (self.width, self.height))
                    frames.append(frame)
                animations[animation_type] = frames
        return animations


    def apply_effect(self, effect_name, duration):
        """Aplikuj efekt na NPC."""
        current_time = pygame.time.get_ticks()

        if effect_name == "slow" and "slow" not in self.effects:
            self.effects["slow"] = current_time + duration
            self.speed /= 2  # Spomalenie na polovicu

        elif effect_name == "overheat" and "overheat" not in self.effects:
            self.effects["overheat"] = {
                "end_time": current_time + duration,
                "last_damage_time": current_time,
                "damage_per_second": 5,
            }

    def knockback(self, direction, distance):
        dx = distance * math.cos(direction)
        dy = distance * math.sin(direction)
        target_x = self.rect.x + dx
        target_y = self.rect.y + dy

        self.knockback_target_pos = pygame.Vector2(target_x, target_y)

    def update(self, player, tmx_data, camera_x, camera_y):
        """Update NPC position and behavior each frame."""

        self.frame_count += 1  # Zvýšte počítadlo frame-ov
        self.camera_x = camera_x
        self.camera_y = camera_y

        # Pohyb iba každý druhý frame
        if self.frame_count % 2 == 0:
            current_time = pygame.time.get_ticks()

            if "overheat" in self.effects:
                overheat_data = self.effects["overheat"]
                if current_time >= overheat_data["last_damage_time"] + 1000:  # Každú sekundu
                    self.take_damage(overheat_data["damage_per_second"], self.floating_text_group)
                    overheat_data["last_damage_time"] = current_time

                # Skontrolujte, či efekt vypršal
                if current_time >= overheat_data["end_time"]:
                    self.effects.pop("overheat")

                # Skontrolujte, či efekt `slow` vypršal
            if "slow" in self.effects and current_time > self.effects["slow"]:
                self.effects.pop("slow")
                self.speed *= 2  # Obnova pôvodnej rýchlosti

            distance_to_player = self.get_distance_to_player(player)

            # Update animation
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time > (1000 * self.animation_speed):
                self.animation_index = (self.animation_index + 1) % len(self.animations[self.current_animation])
                self.image = self.animations[self.current_animation][self.animation_index]
                self.last_frame_time = current_time

            if self.knockback_target_pos:
                current_pos = pygame.Vector2(self.rect.x, self.rect.y)
                direction = self.knockback_target_pos - current_pos

                if direction.length() <= self.knockback_speed:
                    # Snap to target position if close enough
                    self.rect.x, self.rect.y = self.knockback_target_pos.x, self.knockback_target_pos.y

                    # Verify final position is walkable
                    tile_x, tile_y = get_tile_under_player(self.rect, self.tmx_data)
                    tile_properties = get_walk_tile_properties(tile_x, tile_y, self.tmx_data)
                    if not (tile_properties and tile_properties.get("canWalk") == 1):
                        self.knockback_target_pos = None  # Reset knockback if not valid
                    else:
                        self.knockback_target_pos = None  # End knockback
                else:
                    # Move toward the target position
                    direction = direction.normalize() * self.knockback_speed
                    next_x = self.rect.x + direction.x
                    next_y = self.rect.y + direction.y

                    # Check if the intermediate position is walkable
                    next_rect = pygame.Rect(next_x, next_y, self.rect.width, self.rect.height)
                    tile_x, tile_y = get_tile_under_player(next_rect, self.tmx_data)
                    tile_properties = get_walk_tile_properties(tile_x, tile_y, self.tmx_data)

                    if tile_properties and tile_properties.get("canWalk") == 1:
                        self.rect.x += direction.x
                        self.rect.y += direction.y
                    else:
                        self.knockback_target_pos = None  # Cancel knockback if intermediate position is invalid

            if distance_to_player <= self.max_detection_distance:
                if distance_to_player > self.max_approach_distance:
                    direction = self.get_direction_toward_player(player)
                    self.update_orientation(player)
                    if self.can_move_to(direction, tmx_data):
                        self.move_toward_player(direction)
            else:
                if self.current_animation != "Idle":
                    self.current_animation = "Idle"
                    self.animation_index = 0

            if self.check_attack_range(player):
                self.attack(player)



        # Obnovte počítadlo frame-ov každých 60 frame-ov
        if self.frame_count >= 60:
            self.frame_count = 0


    def get_distance_to_player(self, player):
        """Calculate the distance to the player."""
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return pygame.math.Vector2(dx, dy).length()

    def update_orientation(self, player):
        """Update the NPC's orientation based on player's position."""
        if player.rect.centerx < self.rect.centerx:  # Player is to the left
            self.facing_direction = "left"
        else:  # Player is to the right
            self.facing_direction = "right"

        # Update the image to flip horizontally based on facing direction
        if self.facing_direction == "left":
            if self.animations[self.current_animation][self.animation_index]:  # Ensure frames exist
                self.image = pygame.transform.flip(self.animations[self.current_animation][self.animation_index], True,False)
        elif self.facing_direction == "right":
            if self.animations[self.current_animation][self.animation_index]:  # Ensure frames exist
                self.image = self.animations[self.current_animation][self.animation_index]
        else:
            self.image = self.animations[self.current_animation][self.animation_index]

    def get_direction_toward_player(self, player):
        """Calculate the direction toward the player."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        return angle

    def can_move_to(self, direction, tmx_data):
        """Check if the NPC can move to the target position (tile has 'canWalk')."""
        # Calculate potential next position
        next_x = self.rect.x + self.speed * math.cos(direction)
        next_y = self.rect.y + self.speed * math.sin(direction)

        # Get the tile under the potential new position
        tile_x, tile_y = get_tile_under_player(pygame.Rect(next_x, next_y, self.rect.width, self.rect.height), tmx_data)

        # Get the properties of the tile
        tile_properties = get_walk_tile_properties(tile_x, tile_y, tmx_data)

        return tile_properties and tile_properties.get("canWalk") == 1

    def move_toward_player(self, direction):
        """Move NPC toward the player based on the calculated angle."""
        if self.current_animation != "Walk":
            self.current_animation = "Walk"
            self.animation_index = 0  # Reset animation frame to start

        dx = self.speed * math.cos(direction)
        dy = self.speed * math.sin(direction)
        self.rect.x += dx
        self.rect.y += dy

    def check_attack_range(self, player):
        """Check if the NPC is within attack range of the player."""
        distance = self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery
        return pygame.math.Vector2(distance).length() < self.attack_range

    def attack(self, player):
        """Attack the player (damage logic)."""
        current_time = time.time()
        self.current_animation = "Attack"

        # Update NPC's orientation based on the player's position during the attack
        self.update_orientation(player)

        if current_time - self.last_attack_time >= self.attack_cooldown:
            player.health -= self.damage
            if player.health < 0:
                player.health = 0
            self.last_attack_time = current_time  # Update last attack time

    def take_damage(self, damage, floating_text_group):
        """Reduce NPC health and create a floating text."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.drop_item()
            self.kill()

        # Create floating text positioned above the NPC
        floating_text = FloatingText(f"-{damage}", self.rect.centerx, self.rect.centery, 0.5)
        floating_text_group.add(floating_text)

    def drop_item(self):
        """Dropne srdce so šancou 1 ku 25."""
        if random.randint(1, 15) == 1:  # Šanca na drop
            heart = DroppedHeart(self.rect.centerx, self.rect.centery, self.heart_image)
            DroppedHeart.all_hearts.add(heart)

    def draw(self, surface, camera):
        """Draw the NPC considering the camera offset."""
        surface.blit(self.image, self.rect.move(-camera.x, -camera.y))

class NPCManager:
    def __init__(self, floating_text_group, tmx_data, spawn_interval, max_enemies, min_distance, npc_assets, size, hp, damage):
        self.npcs = pygame.sprite.Group()
        self.tmx_data = tmx_data
        self.spawn_interval = spawn_interval
        self.max_enemies = max_enemies  # Maximum number of NPCs allowed
        self.last_spawn_time = time.time()
        self.min_distance = min_distance  # Minimum distance between NPCs
        self.floating_text_group = floating_text_group
        self.npc_assets = npc_assets
        self.size = size
        self.hp = hp
        self.damage = damage

    def check_minimum_distance(self, npc, other_npcs):
        """Ensure the NPC is at least `min_distance` away from all other NPCs."""
        for other_npc in other_npcs:
            if other_npc != npc:  # Skip self-check
                distance = pygame.math.Vector2(
                    npc.rect.centerx - other_npc.rect.centerx,
                    npc.rect.centery - other_npc.rect.centery
                ).length()
                if distance < self.min_distance:
                    return False

    def get_random_walkable_position(self):
        """Get a random walkable position on the map using utils.py functions."""
        walkable_positions = []
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0:  # Ensure the tile is not empty
                        tile_properties = get_walk_tile_properties(x, y, self.tmx_data)
                        if tile_properties and tile_properties.get("canWalk") == 1:
                            walkable_positions.append((x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

        if walkable_positions:
            return random.choice(walkable_positions)
        return None

    def update(self, player, camera_x, camera_y):
        """Update NPCs and spawn new ones at regular intervals."""
        current_time = time.time()
        if current_time - self.last_spawn_time >= self.spawn_interval:
            if len(self.npcs) < self.max_enemies:  # Only spawn if current number of NPCs is less than max
                self.spawn_npc(player)
            self.last_spawn_time = current_time

        # Update all NPCs without camera offset
        for npc in self.npcs:
            npc.update(player, self.tmx_data, camera_x, camera_y)

        DroppedHeart.all_hearts.update(player)

    def spawn_npc(self, player):
        """Spawn a new NPC at a random walkable position far from the player."""
        spawn_pos = self.get_random_walkable_position()
        max_aproach_distance = 40
        max_detection_distance = 300
        if spawn_pos:
            # Check if the spawn position is far enough from the player
            distance_to_player = pygame.math.Vector2(
                spawn_pos[0] - player.rect.centerx,
                spawn_pos[1] - player.rect.centery
            ).length()

            if distance_to_player > max_detection_distance + 100:
                npc = NPC(self.floating_text_group, self.tmx_data, self.size, self.size, self.npc_assets, spawn_pos[0], spawn_pos[1], 1,  max_aproach_distance, max_detection_distance, self.hp, self.damage)
                self.npcs.add(npc)

    def despawn_all_npcs(self):
        """Remove all NPCs from the game."""
        self.npcs.empty()

    def draw(self, surface, camera):
        """Vykreslí NPC a predmety."""
        for npc in self.npcs:
            npc.draw(surface, camera)

        for heart in DroppedHeart.all_hearts:
            surface.blit(heart.image, heart.rect.move(-camera.x, -camera.y))

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, duration=1, color=(255, 0, 0), outline_color=(0, 0, 0), rise_speed=30):
        super().__init__()
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.text = text
        self.color = color
        self.outline_color = outline_color
        self.image = self.create_text_image()
        self.rect = self.image.get_rect()
        self.logical_x = x
        self.logical_y = y
        self.start_y = y
        self.spawn_time = time.time()
        self.duration = duration
        self.rise_speed = rise_speed

    def create_text_image(self):
        """Create text with an outline."""
        text_surface = self.font.render(self.text, True, self.color)
        outline_surface = self.font.render(self.text, True, self.outline_color)
        outlined_image = pygame.Surface((text_surface.get_width() + 2, text_surface.get_height() + 2), pygame.SRCALPHA)
        positions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for pos in positions:
            outlined_image.blit(outline_surface, (1 + pos[0], 1 + pos[1]))
        outlined_image.blit(text_surface, (1, 1))
        return outlined_image

    def update(self, camera_x, camera_y):
        """Update the position, make the text rise, and check expiration."""
        time_elapsed = time.time() - self.spawn_time
        self.logical_y = self.start_y - int(time_elapsed * self.rise_speed)
        self.rect.center = (self.logical_x - camera_x, self.logical_y - camera_y)

        if time_elapsed > self.duration:
            self.kill()

    def draw(self, surface):
        """Draw the floating text."""
        surface.blit(self.image, self.rect)

class DroppedHeart(pygame.sprite.Sprite):
    """Trieda reprezentujúca srdce, ktoré môže hráč zobrať."""
    all_hearts = pygame.sprite.Group()  # Skupina pre všetky srdcia

    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player):
        """Skontroluje, či hráč zobral srdce."""
        if self.rect.colliderect(player.rect):
            player.health = min(player.health + 50, player.max_health)  # Pridanie života hráčovi
            self.kill()

