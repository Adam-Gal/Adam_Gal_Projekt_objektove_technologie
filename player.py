import os
import pygame
import pytmx
from sprite import Sprite
from utils import get_tile_under_player, get_walk_tile_properties, get_structure_tile_properties

class Player(Sprite):
    DIRECTIONS = ["Down", "Up", "Left", "Right"]
    FRAME_DELAY = 10
    BASE_SPEED = 2
    SPRINT_MULTIPLIER = 1.5

    def __init__(self, width, height, asset_path, start_x=0, start_y=0):
        super().__init__(None, width, height)

        self.asset_path = asset_path
        self.animations = self.load_animations()
        self.current_animation = "Down"
        self.current_frame = 0
        self.frame_counter = 0
        self.image = self.animations[self.current_animation][0]

        self.rect.topleft = (start_x, start_y)
        self.speed = self.BASE_SPEED
        self.is_sprinting = False

        # Health and stamina
        self.max_health = 100
        self.health = self.max_health
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.stamina_regen_rate = 0.3
        self.stamina_depletion_rate = 0.25
        self.stamina_recharge_needed = False

        self.teleported = False
        self.new_map = None

        # Bottom half collider
        self.bottom_half_rect = pygame.Rect(
            self.rect.x, self.rect.y + self.rect.height // 2, self.rect.width, self.rect.height // 2
        )

    def load_animations(self):
        animations = {}
        for direction in self.DIRECTIONS:
            path = os.path.join(self.asset_path, direction)
            frames = [self.load_image(os.path.join(path, f"{i}.png")) for i in range(1, 4)]
            animations[direction] = frames
        return animations

    def load_image(self, image_path):
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (self.rect.width, self.rect.height))

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)
        self.bottom_half_rect.move_ip(dx, dy)

    def idle(self):
        self.current_frame = 0
        self.frame_counter = 0
        self.image = self.animations[self.current_animation][0]

    def update_animation(self, direction):
        if direction and direction != self.current_animation:
            self.current_animation = direction
            self.current_frame = 0
            self.frame_counter = 0

        self.frame_counter += 1
        if direction:
            if self.frame_counter >= self.FRAME_DELAY:
                frames = self.animations[self.current_animation]
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.image = frames[self.current_frame]
                self.frame_counter = 0
        else:
            self.idle()

    def handle_movement(self, keys, tmx_data):
        direction, dx, dy = self.get_movement_direction(keys)
        speed = self.adjust_speed_for_sprint(keys, direction)

        if dx != 0 and dy != 0:
            dx, dy = self.normalize_diagonal_movement(dx, dy)

        if self.can_move(dx * speed, dy * speed, tmx_data):
            self.move(dx * speed, dy * speed)

        self.update_animation(direction)

    def get_movement_direction(self, keys):
        direction, dx, dy = None, 0, 0
        if keys[pygame.K_a]:
            dx, direction = -1, "Left"
        if keys[pygame.K_d]:
            dx, direction = 1, "Right"
        if keys[pygame.K_w]:
            dy, direction = -1, "Up"
        if keys[pygame.K_s]:
            dy, direction = 1, "Down"
        return direction, dx, dy

    def adjust_speed_for_sprint(self, keys, moving):
        if moving and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not self.stamina_recharge_needed:
            self.is_sprinting = True
            self.stamina = max(0, self.stamina - self.stamina_depletion_rate)
            if self.stamina == 0:
                self.stamina_recharge_needed = True
            return self.speed * self.SPRINT_MULTIPLIER

        self.is_sprinting = False
        self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate)
        if self.stamina == self.max_stamina:
            self.stamina_recharge_needed = False
        return self.speed

    def normalize_diagonal_movement(self, dx, dy):
        normalization_factor = (2 ** 0.5) / 2
        return dx * normalization_factor, dy * normalization_factor

    def can_move(self, dx, dy, tmx_data):
        new_bottom_half_rect = self.bottom_half_rect.move(dx, dy)
        tile_x, tile_y = get_tile_under_player(new_bottom_half_rect, tmx_data)

        # Skontrolujte, či je pozícia pohybu platná a nezablokuje to pohyb
        if not self.is_tile_walkable(tile_x, tile_y, tmx_data):
            return False

        tile_structure_properties = get_structure_tile_properties(tile_x, tile_y, tmx_data)
        if tile_structure_properties and tile_structure_properties.get("teleport") == 1:
            self.new_map = tile_structure_properties.get("map")
            self.teleported = True
            return False

        return not self.check_collision_with_objects(new_bottom_half_rect, tmx_data)

    def is_tile_walkable(self, tile_x, tile_y, tmx_data):
        properties = get_walk_tile_properties(tile_x, tile_y, tmx_data)
        return properties and properties.get("canWalk") == 1

    def is_teleported(self):
        return self.teleported

    def check_collision_with_objects(self, new_rect, tmx_data):
        for layer in tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    obj_rect = pygame.Rect(
                        obj.x + 10, obj.y + obj.height / 1.5, obj.width - 20, obj.height / 4
                    )
                    if new_rect.colliderect(obj_rect):
                        return True
        return False
