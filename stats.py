import time

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
        if self.player.stamina != self.player.max_stamina:
            # Draw the background for the stamina bar
            pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))  # Background

            # Calculate stamina ratio and color
            stamina_ratio = self.player.stamina / self.player.max_stamina
            bar_color = self.get_stamina_color() if not self.player.stamina_recharge_needed else (128, 128, 128)

            # Draw the stamina bar
            pygame.draw.rect(surface, bar_color, (x, y, width * stamina_ratio, height))

            # Draw black border around the stamina bar
            pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)  # Black border with thickness of 3 pixels


class AbilityDisplay:
    def __init__(self, ability_system):
        self.ability_system = ability_system

        # Načítanie obrázkov do pygame.Surface namiesto reťazcov (stringov)
        self.ability_icons = {
            "Fireball": pygame.image.load("Assets/UI/Fireball.png"),
            "Iceblast": pygame.image.load("Assets/UI/Iceblast.png"),
            "Wind": pygame.image.load("Assets/UI/Wind.png"),
            "Earthspikes": pygame.image.load("Assets/UI/Earthspikes.png"),
        }

        self.ability_colors = {  # Farby pre jednotlivé ability
            "Fireball": (255, 50, 50),  # Červená
            "Iceblast": (50, 150, 255),  # Modrá
            "Wind": (50, 255, 100),  # Zelená
            "Earthspikes": (160, 100, 60)  # Hnedá
        }

        self.icon_size = 50  # Veľkosť ikon
        self.spacing = 10  # Medzera medzi ikonami

    def draw(self, surface, x, y):
        font = pygame.font.SysFont(None, 30)
        selected_ability = self.ability_system.selected_ability
        highlight_color = self.ability_colors.get(selected_ability, (255, 255, 255))  # Default: biela

        for index, ability in enumerate(self.ability_system.abilities):
            icon = self.ability_icons[ability]
            icon_rect = pygame.Rect(x + index * (self.icon_size + self.spacing), y, self.icon_size, self.icon_size)

            # Nakreslenie ikony
            surface.blit(pygame.transform.scale(icon, (self.icon_size, self.icon_size)), icon_rect)

            # Zvýraznenie vybranej ability dvojitým rámom (čierny + farebný)
            if ability == selected_ability:
                pygame.draw.rect(surface, (0, 0, 0), icon_rect.inflate(8, 8), 6)  # Čierny vonkajší rám
                pygame.draw.rect(surface, highlight_color, icon_rect.inflate(4, 4), 4)  # Farebný vnútorný rám

        # Zobrazenie názvu vybratej ability s obrysom
        text = f"Selected: {selected_ability}"
        text_surface = font.render(text, True, highlight_color)  # Hlavný text vo farbe ability
        text_outline = font.render(text, True, (0, 0, 0))  # Obrys (čierny)

        text_x = x
        text_y = y + self.icon_size + 10

        # Nakreslenie obrysu textu (posunuté do štyroch smerov)
        offsets = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        for dx, dy in offsets:
            surface.blit(text_outline, (text_x + dx, text_y + dy))

        # Nakreslenie hlavného textu na vrch obrysu
        surface.blit(text_surface, (text_x, text_y))


class HealthBar:
    def __init__(self, player):
        self.player = player
        self.heart_image = pygame.image.load("Assets/UI/heart.png").convert_alpha()  # Načítanie obrázka srdca
        self.heart_size = 50  # Veľkosť srdca

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

    def draw(self, surface, x, y, width, height):
        """Draw the health bar on the screen."""
        # Pozadie healthbaru
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))

        # Farba healthbaru podľa aktuálneho HP
        health_ratio = self.player.health / self.player.max_health
        bar_color = self.get_health_color()
        pygame.draw.rect(surface, bar_color, (x, y, width * health_ratio, height))

        # Nakreslenie srdca vedľa healthbaru
        heart_x = x - self.heart_size  # Umiestnenie srdca trochu vľavo od healthbaru
        heart_y = y + (height // 2) - (self.heart_size // 2)  # Zarovnanie vertikálne do stredu
        surface.blit(pygame.transform.scale(self.heart_image, (self.heart_size, self.heart_size)), (heart_x, heart_y))

        # Orámovanie healthbaru (čierny rám)
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)  # Čierny rám s hrúbkou 3 pixely


class TimerDisplay:
    def __init__(self, time_limit):
        self.time_limit = time_limit
        self.start_timer = None
        self.font_size = 50  # Väčší font

    def start(self):
        """Spustí časovač."""
        self.start_timer = time.time()

    def reset(self):
        """Resetuje časovač."""
        self.start_timer = None

    def draw(self, surface, x, y):
        """Vykreslí zostávajúci čas na obrazovke."""
        if self.start_timer is not None:
            elapsed_time = time.time() - self.start_timer
            remaining_time = max(0, self.time_limit - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            time_text = f"{minutes:02}:{seconds:02}"

            # Ak zostáva ≤ 15 sekúnd, text sa zmení na červený
            text_color = (255, 0, 0) if remaining_time <= 15 else (255, 255, 255)

            # Načítanie fontu
            font = pygame.font.SysFont(None, self.font_size)
            text_surface = font.render(time_text, True, text_color)

            # Orámovanie - vykreslí text mierne posunutý do všetkých smerov čiernou farbou
            outline_color = (0, 0, 0)
            offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Posunutie na orámovanie

            for dx, dy in offsets:
                shadow_surface = font.render(time_text, True, outline_color)
                surface.blit(shadow_surface, (x + dx, y + dy))

            # Hlavný text navrch
            surface.blit(text_surface, (x, y))

