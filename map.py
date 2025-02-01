import time
import pytmx
import pygame


class Map:
    def __init__(self, tmx_data, time_limit):
        self.tmx_data = tmx_data
        self.controll_panel_on = False
        self.btn_off_count = 0
        self.start_timer = None
        self.time_limit = time_limit
        self.despawn_npcs = False
        self.stopTimer = False

        # Load sound effects
        self.interaction_click_sound = pygame.mixer.Sound("Assets/Sounds/Controll_panel/interaction_click.mp3")
        self.portal_open_sound = pygame.mixer.Sound("Assets/Sounds/Controll_panel/portal_open.mp3")
        self.interaction_click_sound.set_volume(0.4)
        self.portal_open_sound.set_volume(0.8)


    def get_animated_gid(self, tmx_data, gid, elapsed_time):
        # Return the GID for animated tiles based on elapsed time
        tile_properties = tmx_data.get_tile_properties_by_gid(gid)
        if tile_properties and "frames" in tile_properties:
            animation_frames = tile_properties["frames"]
            total_duration = sum(frame[1] for frame in animation_frames)
            if total_duration > 0:
                current_time = elapsed_time % total_duration
                frame_duration_sum = 0
                for frame_gid, duration in animation_frames:
                    frame_duration_sum += duration
                    if current_time < frame_duration_sum:
                        return frame_gid
        return gid

    def render_map_tiles(self, screen, tmx_data, camera, start_time):
        # Render map tiles based on camera position
        tile_width, tile_height = tmx_data.tilewidth, tmx_data.tileheight
        start_x, end_x = max(0, camera.left // tile_width), min(tmx_data.width, (camera.right // tile_width) + 1)
        start_y, end_y = max(0, camera.top // tile_height), min(tmx_data.height, (camera.bottom // tile_height) + 1)

        elapsed_time = (time.time() - start_time) * 1000
        for layer in tmx_data.layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if start_x <= x < end_x and start_y <= y < end_y and gid != 0:
                        gid = self.get_animated_gid(tmx_data, gid, elapsed_time)
                        tile_image = tmx_data.get_tile_image_by_gid(gid)
                        if tile_image:
                            screen.blit(tile_image, (x * tile_width - camera.x, y * tile_height - camera.y))

    def render_map_objects(self, screen, tmx_data, player, camera, start_time):
        # Render map objects above and below the player
        elapsed_time = (time.time() - start_time) * 1000
        above_player, below_player = [], []

        for layer in tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    x_pos, y_pos = obj.x - camera.x, obj.y - camera.y
                    if hasattr(obj, "gid"):
                        gid = self.get_animated_gid(tmx_data, obj.gid, elapsed_time)
                        tile_image = tmx_data.get_tile_image_by_gid(gid)
                        if tile_image:
                            (above_player if y_pos + obj.height / 2 < player.rect.centery - camera.y else below_player).append((tile_image, x_pos, y_pos))
                    else:
                        (above_player if y_pos + obj.height / 2 < player.rect.centery - camera.y else below_player).append((None, x_pos, y_pos))

        for tile_image, x_pos, y_pos in above_player:
            screen.blit(tile_image, (x_pos, y_pos)) if tile_image else pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(x_pos, y_pos, 50, 50), 2)
        screen.blit(player.image, player.rect.move(-camera.x, -camera.y))
        for tile_image, x_pos, y_pos in below_player:
            screen.blit(tile_image, (x_pos, y_pos)) if tile_image else pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(x_pos, y_pos, 50, 50), 2)

    def turn_on_buttons(self):
        # Activate buttons, change animations, and start fight music
        pygame.mixer.music.load("Assets/Sounds/Music/fight_music.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)
        elapsed_time = (time.time() - time.time()) * 1000
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Structures":
                for obj in layer:
                    if hasattr(obj, 'properties') and 'button' in obj.properties:
                        current_gid = obj.gid
                        current_gid = self.get_animated_gid(self.tmx_data, current_gid, elapsed_time)
                        tile_properties = self.tmx_data.get_tile_properties_by_gid(current_gid)
                        if tile_properties and 'frames' in tile_properties and obj.properties['button'] == 0:
                            animation_frames = tile_properties['frames']
                            next_frame_gid = animation_frames[1][0]
                            obj.gid = next_frame_gid
                            obj.properties['button'] = 1
        self.interaction_click_sound.play()

    def turn_off_button(self, player_rect):
        # Turn off button which ist close enough to player
        elapsed_time = (time.time() - time.time()) * 1000
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Structures":
                for obj in layer:
                    if hasattr(obj, 'properties') and 'button' in obj.properties:
                        obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        if player_rect.colliderect(obj_rect.inflate(10, 10)):
                            if obj.properties['button']:
                                current_gid = self.get_animated_gid(self.tmx_data, obj.gid, elapsed_time)
                                tile_properties = self.tmx_data.get_tile_properties_by_gid(current_gid)
                                if tile_properties and 'frames' in tile_properties:
                                    animation_frames = tile_properties['frames']
                                    obj.gid = animation_frames[1][0]  # Vypnutý stav
                                    obj.properties['button'] = 0
                                    self.btn_off_count += 1
                                    self.update_control_panel_animation()
                                    self.interaction_click_sound.play()
                                    if self.btn_off_count >= 3:
                                        self.portal_open_sound.play()
                                        pygame.mixer.music.load("Assets/Sounds/Music/background_music.mp3")
                                        pygame.mixer.music.set_volume(0.1)
                                        pygame.mixer.music.play(-1)
                                        self.activate_teleport(self.tmx_data)
                                        self.btn_off_count = 0
                                        self.controllPanelOn = False
                                        self.start_timer = None  # Reset časovačas
                                        self.despawn_npcs = True
                                        self.stopTimer = True

    def update_control_panel_animation(self):
        # Change control panel animation based on how many buttons are pressed
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Structures":
                for obj in layer:
                    if hasattr(obj, 'properties') and 'controllPanel' in obj.properties and obj.properties['controllPanel'] < 3:
                        tile_properties = self.tmx_data.get_tile_properties_by_gid(obj.gid)
                        if tile_properties and 'frames' in tile_properties:
                            animation_frames = tile_properties['frames']
                            next_frame_gid = animation_frames[1][0]
                            obj.properties['controllPanel'] += 1
                            obj.gid = next_frame_gid

    def is_near_control_panel(self, player_rect):
        # Check if the player is near an object with 'controllPanel = 1' in the 'Structures' layer
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "Structures":
                    for obj in layer:
                        if hasattr(obj, 'properties') and 'controllPanel' in obj.properties and obj.properties['controllPanel'] == 0:
                            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            if player_rect.colliderect(obj_rect.inflate(10, 10)):  # Adjust the inflate value as needed
                                return True
        return False

    def is_near_button(self, player_rect):
        """Check if the player is near a button in the 'Structures' layer."""
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "Structures":
                    for obj in layer:
                        if hasattr(obj, 'properties') and 'button' in obj.properties:
                            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            if player_rect.colliderect(obj_rect.inflate(10, 10)):  # Adjust the inflate value as needed
                                return True
        return False

    def reset_control_panel(self, player):
        # Reset the control panel and buttons after the time limit
        if self.controll_panel_on and self.start_timer is not None:
            elapsed_time = time.time() - self.start_timer
            if elapsed_time > self.time_limit or player.is_dead:
                for layer in self.tmx_data.layers:
                    if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Structures":
                        for obj in layer:
                            if hasattr(obj, 'properties'):
                                if 'button' in obj.properties and obj.properties['button'] == 1:
                                    obj.properties['button'] = 0  # Reset tlačidiel
                                    tile_properties = self.tmx_data.get_tile_properties_by_gid(obj.gid)
                                    if tile_properties and 'frames' in tile_properties:
                                        animation_frames = tile_properties['frames']
                                        obj.gid = animation_frames[1][0]  # Prepnúť späť na vypnutý stav
                                if 'controllPanel' in obj.properties:
                                    tile_properties = self.tmx_data.get_tile_properties_by_gid(obj.gid)
                                    if tile_properties and 'frames' in tile_properties:
                                        animation_frames = tile_properties['frames']
                                        obj.gid = animation_frames[2][0]  # Prepnúť späť na pôvodný stav
                                        obj.properties['controllPanel'] = 0
                self.btn_off_count = 0
                self.controll_panel_on = False
                self.start_timer = None
                pygame.mixer.music.load("Assets/Sounds/Music/background_music.mp3")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.1)
                self.interaction_click_sound.play()

    def activate_teleport(self, tmx_data):
        # Activate the teleporter after all button are pressed before time limit
        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0:
                        tile_properties = tmx_data.get_tile_properties_by_gid(gid)
                        if tile_properties and 'frames' in tile_properties and 'teleport' in tile_properties:
                            animation_frames = tile_properties['frames']
                            if len(animation_frames) > 1:
                                new_gid = animation_frames[1][0]  # Použite správny index na získanie GID
                                layer.data[y][x] = new_gid  # Aktualizujte iba potrebné GID
                                tile_properties['teleport'] = 1