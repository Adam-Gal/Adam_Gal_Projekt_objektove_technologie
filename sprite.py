import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height)) if image is None else pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
