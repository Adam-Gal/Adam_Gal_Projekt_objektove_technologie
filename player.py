import os
import pygame
import pytmx

from sprite import Sprite
from utils import get_tile_under_player, get_tile_properties


class Player(Sprite):
    def __init__(self, width, height, asset_path, start_x=0, start_y=0):
        super().__init__(None, width, height)
        self.asset_path = asset_path
        self.animations = self.load_animations()
        self.current_animation = "Down"
        self.current_frame = 0
        self.frame_delay = 10
        self.frame_counter = 0
        self.image = self.animations[self.current_animation][0]

        self.facing_direction = "Down"
        self.rect.topleft = (start_x, start_y)
        self.speed = 2
        self.is_sprinting = False

        # Health attributes
        self.max_health = 100
        self.health = self.max_health

        # Stamina attributes
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.stamina_regen_rate = 0.3
        self.stamina_depletion_rate = 0.35
        self.stamina_recharge_needed = False

        # Set up a collider for the player that only considers the bottom half
        self.bottom_half_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height // 2, self.rect.width, self.rect.height // 2)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.bottom_half_rect.x = self.rect.x
        self.bottom_half_rect.y = self.rect.y + self.rect.height // 2


    def load_animations(self):
        animations = {}
        directions = ["Down", "Up", "Left", "Right"]
        for direction in directions:
            path = os.path.join(self.asset_path, direction)
            frames = [os.path.join(path, f"{i}.png") for i in range(1, 4)]
            animations[direction] = [self.load_image(frame) for frame in frames]
        return animations

    def load_image(self, image_path):
        try:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (self.rect.width, self.rect.height))
        except pygame.error as e:
            raise SystemExit(f"Unable to load image {image_path}: {e}")

    def idle(self):
        self.current_frame = 0  # Reset to the first frame
        self.frame_counter = 0  # Reset frame counter
        self.image = self.animations[self.current_animation][0]  # Set the current image to the first frame

    def update(self, direction):
        if direction:
            # If the direction has changed, reset to the first frame
            if self.current_animation != direction:
                self.current_frame = 0
                self.frame_counter = 0

            self.facing_direction = direction
            self.current_animation = direction

            # Animation frames
            animation_frames = self.animations[direction]
            extended_frames = [animation_frames[0], animation_frames[1], animation_frames[0], animation_frames[2]]

            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(extended_frames)
                self.frame_counter = 0

            self.image = extended_frames[self.current_frame]
        else:
            self.idle()

    def handle_movement(self, keys, tmx_data):
        """Handle player movement and stamina."""
        direction = None
        dx, dy = 0, 0
        moving = False  # Indicator to check if the player is moving

        # Base speed (adjusted for sprinting)
        speed = self.speed

        # Handle movement based on key presses
        if keys[pygame.K_a]:
            dx = -1
            direction = "Left"
            moving = True
        if keys[pygame.K_d]:
            dx = 1
            direction = "Right"
            moving = True
        if keys[pygame.K_w]:
            dy = -1
            direction = "Up"
            moving = True
        if keys[pygame.K_s]:
            dy = 1
            direction = "Down"
            moving = True

        # Normalize diagonal movement to prevent faster diagonal speed
        if dx != 0 and dy != 0:
            normalization_factor = (2 ** 0.5) / 2
            dx *= normalization_factor
            dy *= normalization_factor

        # Sprint logic
        if moving and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not self.stamina_recharge_needed:
            self.is_sprinting = True
            speed *= 1.5  # Increase speed during sprint
            self.stamina -= self.stamina_depletion_rate
            self.stamina = max(0, self.stamina)
            if self.stamina == 0:
                self.stamina_recharge_needed = True
        else:
            self.is_sprinting = False
            self.stamina += self.stamina_regen_rate
            self.stamina = min(self.max_stamina, self.stamina)
            if self.stamina == self.max_stamina:
                self.stamina_recharge_needed = False

        # Calculate the player's new position
        new_rect = self.rect.move(dx * speed, dy * speed)
        new_bottom_half_rect = self.bottom_half_rect.move(dx * speed, dy * speed)

        # Get the tile under the bottom half of the player
        tile_x, tile_y = get_tile_under_player(new_bottom_half_rect, tmx_data)
        tile_properties = get_tile_properties(tile_x, tile_y, tmx_data)

        # Special check for downward movement
        if direction == "Down":
            # Check the bottom tile (based on the bottom of the player's sprite)
            bottom_tile_y = (new_bottom_half_rect.bottom - 1) // tmx_data.tileheight
            bottom_tile_properties = get_tile_properties(tile_x, bottom_tile_y, tmx_data)
            if not (bottom_tile_properties and "canWalk" in bottom_tile_properties and bottom_tile_properties[
                "canWalk"] == 1):
                # If the bottom tile is not walkable, prevent downward movement
                dy = 0

        # Check if there's a collision with any objects at the new position
        if tile_properties and "canWalk" in tile_properties and tile_properties[
            "canWalk"] == 1 and not self.check_collision_with_objects(new_bottom_half_rect, tmx_data):
            self.move(dx * speed, dy * speed)

        # Update the animation based on the current direction
        self.update(direction)

    def check_collision_with_objects(self, new_rect, tmx_data):
        """Check if the player collides with an object at the new position."""
        for layer in tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    obj_rect = pygame.Rect(obj.x+10, obj.y+obj.height/1.5, obj.width-20, obj.height / 4)

                    # Check if the new rect would collide with any object
                    if new_rect.colliderect(obj_rect):
                        return True
        return False

