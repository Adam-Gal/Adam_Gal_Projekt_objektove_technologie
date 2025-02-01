import os
import pygame

def load_animations(base_path, width, height):
    animations = {}
    for animation_type in os.listdir(base_path):
        animation_path = os.path.join(base_path, animation_type)
        if os.path.isdir(animation_path):
            frames = []
            for filename in sorted(os.listdir(animation_path), key=lambda x: int(''.join(filter(str.isdigit, x)))):
                frame_path = os.path.join(animation_path, filename)
                frame = pygame.image.load(frame_path)
                frame = pygame.transform.scale(frame, (width, height))
                frames.append(frame)
            animations[animation_type] = frames
    return animations

def load_animation_frames(animation_path, width=None, height=None):
    frames = []
    # List all files in the directory and sort them (you can adjust sorting as needed)
    for filename in sorted(os.listdir(animation_path)):
        file_path = os.path.join(animation_path, filename)
        if os.path.isfile(file_path) and file_path.endswith('.png'):
            image = pygame.image.load(file_path).convert_alpha()
            # Check if the size is provided, if not set the size of the first image
            if not width or not height:
                width, height = image.get_size()
            # Scale the image to the specified width and height
            image = pygame.transform.scale(image, (width, height))
            frames.append(image)
    return frames
