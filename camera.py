import pygame

class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height, camera_speed=0.1):
        self.camera = pygame.Rect(0, 0, screen_width, screen_height)
        self.map_width = map_width
        self.map_height = map_height
        self.camera_speed = camera_speed

    def update(self, target_rect):
        target_pos = pygame.Vector2(
            target_rect.centerx - self.camera.width // 2,
            target_rect.centery - self.camera.height // 2
        )
        # Smooth camera movement towards target
        self.camera.x += (target_pos.x - self.camera.x) * self.camera_speed
        self.camera.y += (target_pos.y - self.camera.y) * self.camera_speed

        # Constrain the camera to map boundaries
        self.camera.left = max(0, self.camera.left)
        self.camera.top = max(0, self.camera.top)
        self.camera.right = min(self.map_width, self.camera.right)
        self.camera.bottom = min(self.map_height, self.camera.bottom)

    def apply(self, rect):
        return rect.move(-self.camera.topleft)

    def get_offset(self):
        return self.camera.topleft