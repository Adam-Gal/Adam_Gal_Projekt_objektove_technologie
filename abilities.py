import pygame
import os

class Ability(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.velocity = (0, 0)  # Default value to prevent AttributeError

    def update(self):
        pass  # Can be overridden in specific ability classes

class Fireball(Ability):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.image_folder = "Assets/Abilities/Fire/"
        self.image_paths = sorted([os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if f.startswith("FB") and f.endswith(".png")])

        self.images = [pygame.image.load(path).convert_alpha() for path in self.image_paths]
        self.current_frame = 0
        self.animation_speed = 100
        self.last_animation_time = pygame.time.get_ticks()

        self.speed = 10
        self.velocity = self.get_velocity_from_direction(direction)
        self.rect = self.adjust_hitbox(x, y, direction)
        self.images = [self.rotate_image(img, direction) for img in self.images]
        self.image = self.images[self.current_frame]

    def get_velocity_from_direction(self, direction):
        if direction == "Up":
            return 0, -self.speed
        elif direction == "Down":
            return 0, self.speed
        elif direction == "Left":
            return -self.speed, 0
        elif direction == "Right":
            return self.speed, 0
        elif direction == "UpLeft":
            return -self.speed * 0.707, -self.speed * 0.707
        elif direction == "UpRight":
            return self.speed * 0.707, -self.speed * 0.707
        elif direction == "DownLeft":
            return -self.speed * 0.707, self.speed * 0.707
        elif direction == "DownRight":
            return self.speed * 0.707, self.speed * 0.707
        return 0, 0

    def adjust_hitbox(self, x, y, direction):
        width, height = self.images[0].get_size()
        if direction == "Up" or direction == "Down":
            width, height = height, width
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (x, y)
        return rect

    def rotate_image(self, image, direction):
        if direction == "Up":
            return pygame.transform.rotate(image, 90)
        elif direction == "Down":
            return pygame.transform.rotate(image, 270)
        elif direction == "Left":
            return pygame.transform.rotate(image, 180)
        return image

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation_time > self.animation_speed:
            self.last_animation_time = current_time
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]

    def draw(self, screen, show_hitboxes=False):
        screen.blit(self.image, self.rect)
        if show_hitboxes:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

class IceBlast(Ability):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.image = pygame.Surface((15, 15))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        if self.direction == "Up":
            self.velocity = (0, -self.speed)
        elif self.direction == "Down":
            self.velocity = (0, self.speed)
        elif self.direction == "Left":
            self.velocity = (-self.speed, 0)
        elif self.direction == "Right":
            self.velocity = (self.speed, 0)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

class AbilitySystem:
    def __init__(self):
        self.abilities = pygame.sprite.Group()
        self.last_used = {
            "fireball": pygame.time.get_ticks(),
            "iceblast": pygame.time.get_ticks(),
        }
        self.cooldowns = {
            "fireball": 1000,  # Fireball cooldown: 1 second
            "iceblast": 5000,  # Iceblast cooldown: 5 seconds
        }
        self.available_abilities = ["fireball", "iceblast"]
        self.selected_ability_index = 0
        self.selected_ability = self.available_abilities[self.selected_ability_index]
        self.last_selection_time = pygame.time.get_ticks()
        self.selection_delay = 200  # Milliseconds between ability changes

    def cycle_ability(self, direction):
        """Cycle through available abilities."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_selection_time > self.selection_delay:
            self.last_selection_time = current_time

            if direction == "next":
                self.selected_ability_index = (self.selected_ability_index + 1) % len(self.available_abilities)
            elif direction == "prev":
                self.selected_ability_index = (self.selected_ability_index - 1) % len(self.available_abilities)

            self.selected_ability = self.available_abilities[self.selected_ability_index]

    def trigger_ability(self, player_x, player_y, facing_direction):
        """Trigger the currently selected ability."""
        current_time = pygame.time.get_ticks()

        if self.selected_ability == "fireball" and current_time - self.last_used["fireball"] >= self.cooldowns["fireball"]:
            self.last_used["fireball"] = current_time
            fireball = Fireball(player_x, player_y, facing_direction)
            self.abilities.add(fireball)

        if self.selected_ability == "iceblast" and current_time - self.last_used["iceblast"] >= self.cooldowns["iceblast"]:
            self.last_used["iceblast"] = current_time
            iceblast = IceBlast(player_x, player_y, facing_direction)
            self.abilities.add(iceblast)

    def update_abilities(self):
        for ability in self.abilities:
            ability.update()

    def draw_abilities(self, screen):
        for ability in self.abilities:
            screen.blit(ability.image, ability.rect)
