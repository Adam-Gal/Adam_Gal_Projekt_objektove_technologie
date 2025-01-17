import os
import pygame
from sprite import Sprite

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

        self.facing_direction = "Down"  # Default facing direction
        self.rect.topleft = (start_x, start_y)
        self.speed = 3
        self.is_sprinting = False

        # Stamina-related attributes
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.stamina_regen_rate = 0.3
        self.stamina_depletion_rate = 0.4
        self.stamina_recharge_needed = False

    def load_animations(self):
        """Load animations for each direction."""
        animations = {}
        directions = ["Down", "Up", "Left", "Right"]
        for direction in directions:
            path = os.path.join(self.asset_path, direction)
            frames = [os.path.join(path, f"{i}.png") for i in range(1, 4)]
            animations[direction] = [self.load_image(frame) for frame in frames]
        return animations

    def load_image(self, image_path):
        """Load an image and scale it to the player's size."""
        try:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (self.rect.width, self.rect.height))
        except pygame.error as e:
            raise SystemExit(f"Unable to load image {image_path}: {e}")

    def move(self, dx, dy):
        """Move the player by the specified deltas."""
        self.rect.x += dx
        self.rect.y += dy

    def idle(self):
        """Set the player to an idle state."""
        self.current_frame = 0  # Reset to the first frame
        self.frame_counter = 0  # Reset frame counter
        self.image = self.animations[self.current_animation][0]  # Set the current image to the first frame

    def update(self, direction):
        """Update the player's animation based on the current direction."""
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

    def handle_movement(self, keys):
        """Handle player movement and stamina."""
        direction = None
        dx, dy = 0, 0
        speed = self.speed

        # Sprint logic
        moving = False
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

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            normalization_factor = (2 ** 0.5) / 2
            dx *= normalization_factor
            dy *= normalization_factor

        if moving and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not self.stamina_recharge_needed:
            self.is_sprinting = True
            speed *= 1.5
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

        # Move player
        self.move(dx * speed, dy * speed)

        # Update animation based on direction
        self.update(direction)

    def draw(self, screen, camera_x, camera_y):
        """Draw the player adjusted for the camera position."""
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
