from enum import Enum

import libtcodpy as libtcod
from libtcodpy import Color
from map.tile import Tiles


def generate_tile_dict(room_floor, room_wall, corridor_floor, corridor_wall, cave_floor, cave_wall, door,
                       unknown=libtcod.black):
    return {
        Tiles.ROOM_FLOOR:     room_floor,
        Tiles.ROOM_WALL:      room_wall,
        Tiles.CORRIDOR_FLOOR: corridor_floor,
        Tiles.CORRIDOR_WALL:  corridor_wall,
        Tiles.CAVE_FLOOR:     cave_floor,
        Tiles.CAVE_WALL:      cave_wall,
        Tiles.DOOR:           door,
        None:                 unknown
    }


def generate_monochrome_dict(color):
    return generate_tile_dict(color, color, color, color, color, color, color)


def color_dict_change_brightness(color_dict, mod):
    copy = color_dict.copy()
    for key in copy.keys():
        if mod > 0:
            copy[key] = copy[key].__add__(Color(mod, mod, mod))
        else:
            copy[key] = copy[key].__sub__(Color(-mod, -mod, -mod))
    return copy


# A convenience method that allows color dicts to be modified when initialized in the ColorSchemes enum
def set_tile_color(color_dict, tile, color):
    copy = color_dict.copy()
    copy[tile] = color
    return copy


DEFAULT_COLORS = generate_tile_dict(libtcod.light_blue, libtcod.dark_blue, libtcod.gray, libtcod.darker_gray,
                                    libtcod.darker_orange, libtcod.darkest_orange, libtcod.dark_cyan)


class ColorScheme:
    def __init__(self, foreground=DEFAULT_COLORS, background=DEFAULT_COLORS, memory_brightness_mod=32, allow_fade=True):
        self.background = background if background else generate_monochrome_dict(libtcod.black)
        self.foreground = foreground if foreground else background
        self.memory_brightness_mod = memory_brightness_mod
        self.allow_fade = allow_fade

    def get_memory_color(self, color):
        return color.__sub__(Color(self.memory_brightness_mod, self.memory_brightness_mod, self.memory_brightness_mod))


class ColorSchemes(Enum):
    CLASSIC = ColorScheme(foreground=set_tile_color(generate_monochrome_dict(libtcod.lightest_gray), Tiles.DOOR,
                                                    libtcod.dark_yellow), background=None, memory_brightness_mod=64,
                          allow_fade=False)
    CLASSIC_COLORED = ColorScheme(foreground=color_dict_change_brightness(DEFAULT_COLORS, 32), background=None,
                                  allow_fade=False)
    SOLID = ColorScheme()
    COMBO = ColorScheme(foreground=color_dict_change_brightness(DEFAULT_COLORS, 32))