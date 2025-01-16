import pygame
import os


# Base class for abilities
class Ability(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.velocity = (0, 0)  # Default value to prevent AttributeError

    def update(self):
        pass  # Can be overridden in specific ability classes

    def adjust_hitbox(self, x, y, direction):
        """Adjusts the hitbox based on the ability's direction."""
        # Assume width and height of the image
        width, height = 20, 20  # Default size for a generic ability
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (x, y)
        return rect

    def set_velocity(self, direction, speed):
        """Sets the velocity based on the direction."""
        if direction == "Up":
            return (0, -speed)
        elif direction == "Down":
            return (0, speed)
        elif direction == "Left":
            return (-speed, 0)
        elif direction == "Right":
            return (speed, 0)
        return (0, 0)


# Fireball ability
class Fireball(Ability):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)

        # Load fireball images for different directions
        self.image_folder = "Assets/Abilities/Fire/"
        self.image_paths = sorted([os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if
                                   f.startswith("FB") and f.endswith(".png")])

        # Load images and set up animation
        self.images = [pygame.image.load(path).convert_alpha() for path in self.image_paths]

        if not self.images:
            print("Error: No images found for fireball!")
            return  # Exit if no images are found, avoiding further errors

        self.current_frame = 0
        self.animation_speed = 100  # Milliseconds per frame
        self.last_animation_time = pygame.time.get_ticks()

        self.speed = 10  # Movement speed of the fireball
        self.velocity = self.set_velocity(direction, self.speed)

        # Make sure to rotate images and set the initial image here
        self.images = [self.rotate_image(img, direction) for img in self.images]
        self.image = self.images[self.current_frame]  # Set the initial image

        # Now that self.image is assigned, call adjust_hitbox
        self.rect = self.adjust_hitbox(x, y, direction)

    def rotate_image(self, image, direction):
        """Rotates the image based on the direction."""
        if direction == "Left":
            return pygame.transform.rotate(image, 180)
        elif direction == "Right":
            return pygame.transform.rotate(image, 0)
        elif direction == "Up":
            return pygame.transform.rotate(image, 90)
        elif direction == "Down":
            return pygame.transform.rotate(image, -90)
        return image

    def update(self):
        """Update the fireball's position and animation."""
        # Move the fireball based on its velocity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Update the animation
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation_time > self.animation_speed:
            self.last_animation_time = current_time
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]  # Update the fireball image

    def draw(self, screen, show_hitboxes=False):
        """Draw the fireball on the screen."""
        screen.blit(self.image, self.rect)
        if show_hitboxes:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


# Ability System to manage multiple abilities
class AbilitySystem:
    def __init__(self):
        self.abilities = pygame.sprite.Group()  # Holds all active abilities
        self.selected_ability = "Fireball"  # The current ability to use (can be switched)
        self.last_ability_time = 0  # To track the time of the last ability trigger
        self.ability_cooldown = 500  # Cooldown time between abilities in milliseconds

    def cycle_ability(self, direction):
        """Cycles through the available abilities."""
        if direction == "next":
            if self.selected_ability == "Fireball":
                self.selected_ability = "Iceblast"  # Example, can add more abilities
            elif self.selected_ability == "Iceblast":
                self.selected_ability = "Fireball"
        elif direction == "prev":
            if self.selected_ability == "Fireball":
                self.selected_ability = "Iceblast"
            elif self.selected_ability == "Iceblast":
                self.selected_ability = "Fireball"

    def trigger_ability(self, x, y, direction):
        """Trigger the selected ability at the player's position and direction, with a delay."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_ability_time >= self.ability_cooldown:
            if self.selected_ability == "Fireball":
                fireball = Fireball(x, y, direction)
                self.abilities.add(fireball)  # Add the new fireball to the abilities group
            # You can add more abilities like Iceblast, Lightning, etc., in a similar way
            self.last_ability_time = current_time  # Update the last ability time

    def update_abilities(self):
        """Update all active abilities."""
        self.abilities.update()

    def draw_abilities(self, screen, camera_x, camera_y):
        """Draw all active abilities on the screen."""
        for ability in self.abilities:
            screen.blit(ability.image, ability.rect.move(-camera_x, -camera_y))
