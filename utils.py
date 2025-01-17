# utils.py
import pytmx

def get_tile_under_player(player_rect, tmx_data):
    """Get the tile position under the player."""
    tile_width = tmx_data.tilewidth
    tile_height = tmx_data.tileheight

    # Calculate the tile coordinates (row, col)
    tile_x = player_rect.centerx // tile_width
    tile_y = player_rect.centery // tile_height

    return tile_x, tile_y

def get_tile_properties(tile_x, tile_y, tmx_data):
    """Get the properties of the tile under the player."""
    tile_layer = tmx_data.get_layer_by_name("Ground")
    gid = tile_layer.data[tile_y][tile_x]
    if gid != 0:
        tile_properties = tmx_data.get_tile_properties_by_gid(gid)
        return tile_properties
    return None
