import pygame

class StaminaBar:
    def __init__(self, player):
        self.player = player

    def get_stamina_color(self):
        """Get color based on stamina level with smooth transitions."""
        ratio = self.player.stamina / self.player.max_stamina
        if ratio > 0.5:
            transition_ratio = (ratio - 0.5) * 2
            r = int(255 * (1 - transition_ratio))
            g = 255
            b = 0
        else:
            transition_ratio = ratio * 2
            r = 255
            g = int(255 * transition_ratio)
            b = 0
        return (r, g, b)

    def update(self):
        """Update logic for stamina (if needed)."""
        pass

    def draw(self, surface, x, y, width, height):
        """Draw the stamina bar on the screen."""
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))  # Background
        stamina_ratio = self.player.stamina / self.player.max_stamina
        bar_color = self.get_stamina_color() if not self.player.stamina_recharge_needed else (128, 128, 128)
        pygame.draw.rect(surface, bar_color, (x, y, width * stamina_ratio, height))


class SelectedAbilityDisplay:
    def __init__(self, ability_system):
        self.ability_system = ability_system

    def draw(self, surface, x, y):
        """Draw the currently selected ability."""
        font = pygame.font.SysFont(None, 30)
        ability_name = self.ability_system.selected_ability.capitalize()
        text = font.render(f"Selected Ability: {ability_name}", True, (255, 255, 255))
        surface.blit(text, (x, y))


class HealthBar:
    def __init__(self, player):
        self.player = player

    def get_health_color(self):
        """Get color based on health level with smooth transitions."""
        ratio = self.player.health / self.player.max_health
        if ratio > 0.5:
            transition_ratio = (ratio - 0.5) * 2
            r = int(255 * (1 - transition_ratio))
            g = 255
            b = 0
        else:
            transition_ratio = ratio * 2
            r = 255
            g = int(255 * transition_ratio)
            b = 0
        return (r, g, b)

    def update(self):
        """Update logic for health (if needed)."""
        pass

    def draw(self, surface, x, y, width, height):
        """Draw the health bar on the screen."""
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))  # Background
        health_ratio = self.player.health / self.player.max_health
        bar_color = self.get_health_color()
        pygame.draw.rect(surface, bar_color, (x, y, width * health_ratio, height))
