import math
import pygame
import random
import pytmx
import time
from utils import get_tile_under_player, get_walk_tile_properties


class NPC(pygame.sprite.Sprite):
    def __init__(self, width, height, asset_path, start_x=0, start_y=0, attack_cooldown=1, max_approach_distance=40, max_detection_distance=400):
        super().__init__()
        self.asset_path = asset_path
        self.image = pygame.image.load(self.asset_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (start_x, start_y)
        self.speed = 1.5
        self.attack_range = 40  # Range in pixels to attack the player
        self.health = 50
        self.damage = 10
        self.attack_cooldown = attack_cooldown  # Cooldown period in seconds
        self.last_attack_time = 0  # Last time an attack was made (in seconds)
        self.max_approach_distance = max_approach_distance  # Minimum distance NPC can get to the player
        self.max_detection_distance = max_detection_distance  # Maximum distance NPC can detect the player

    def update(self, player, tmx_data):
        """Update NPC position and behavior each frame."""
        # Get the distance to the player
        distance_to_player = self.get_distance_to_player(player)

        # Check if the NPC is within detection range (max_detection_distance)
        if distance_to_player <= self.max_detection_distance:
            # If within detection range and the player is not too close
            if distance_to_player > self.max_approach_distance:
                direction = self.get_direction_toward_player(player)
                self.update_orientation(player)  # Update orientation based on player's position

                # Move NPC toward the player if possible
                if self.can_move_to(direction, tmx_data):  # Check if NPC can move
                    self.move_toward_player(direction)

        # Check for collisions with obstacles
        if self.check_collision_with_objects(tmx_data):
            self.avoid_obstacles(tmx_data)

        # Attack player if within range and cooldown has passed
        if self.check_attack_range(player):
            self.attack(player)

    def get_distance_to_player(self, player):
        """Calculate the distance to the player."""
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return pygame.math.Vector2(dx, dy).length()

    def update_orientation(self, player):
        """Flip NPC sprite based on player's relative position."""
        if player.rect.centerx < self.rect.centerx:  # Player is to the right
            self.image = pygame.transform.flip(pygame.image.load(self.asset_path), True, False)
        else:  # Player is to the left
            self.image = pygame.transform.flip(pygame.image.load(self.asset_path), False, False)
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

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
        dx = self.speed * math.cos(direction)
        dy = self.speed * math.sin(direction)
        self.rect.x += dx
        self.rect.y += dy

    def avoid_obstacles(self, tmx_data):
        """Make the NPC avoid obstacles."""
        self.rect.x += random.choice([-self.speed, self.speed])
        self.rect.y += random.choice([-self.speed, self.speed])

    def check_collision_with_objects(self, tmx_data):
        """Check if NPC collides with any objects."""
        for layer in tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    obj_rect = pygame.Rect(obj.x + 10, obj.y + obj.height / 1.5, obj.width - 20, obj.height / 4)
                    if self.rect.colliderect(obj_rect):
                        return True
        return False

    def check_attack_range(self, player):
        """Check if the NPC is within attack range of the player."""
        distance = self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery
        return pygame.math.Vector2(distance).length() < self.attack_range

    def attack(self, player):
        """Attack the player (damage logic)."""
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            player.health -= self.damage
            if player.health < 0:
                player.health = 0
            self.last_attack_time = current_time  # Update last attack time

    def draw(self, surface, camera):
        """Draw the NPC considering the camera offset."""
        surface.blit(self.image, self.rect.move(-camera.x, -camera.y))

class NPCManager:
    def __init__(self, tmx_data, spawn_interval=1, max_enemies=5, min_distance=50):
        self.npcs = pygame.sprite.Group()
        self.tmx_data = tmx_data
        self.spawn_interval = spawn_interval
        self.max_enemies = max_enemies  # Maximum number of NPCs allowed
        self.last_spawn_time = time.time()
        self.min_distance = min_distance  # Minimum distance between NPCs

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

    def update(self, player, camera):
        """Update NPCs and spawn new ones at regular intervals."""
        current_time = time.time()
        if current_time - self.last_spawn_time >= self.spawn_interval:
            if len(self.npcs) < self.max_enemies:  # Only spawn if current number of NPCs is less than max
                self.spawn_npc()
            self.last_spawn_time = current_time

        # Update all NPCs without camera offset
        for npc in self.npcs:
            npc.update(player, self.tmx_data)

    def spawn_npc(self):
        """Spawn a new NPC at a random walkable position."""
        spawn_pos = self.get_random_walkable_position()
        if spawn_pos:
            npc = NPC(50, 50, "npc1.png", spawn_pos[0], spawn_pos[1])
            self.npcs.add(npc)

    def despawn_all_npcs(self):
        """Remove all NPCs from the game."""
        self.npcs.empty()

    def draw(self, surface, camera):
        """Draw all NPCs considering the camera offset."""
        for npc in self.npcs:
            npc.draw(surface, camera)
