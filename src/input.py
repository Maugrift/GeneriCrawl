from enum import Enum

import libtcodpy as libtcod
from game_states import GameStates


def apply_modifiers(key, action):
    if 'direction' in action.keys():
        if key.shift:
            action['face'] = True
            action['move'] = False
        elif key.lctrl:
            action['face'] = False
            action['move'] = True
        else:
            action['face'] = True
            action['move'] = True

    return action


class KeyMap:
    def __init__(self, vk_key_map, chr_key_map):
        self.vk_key_map = vk_key_map
        self.chr_key_map = chr_key_map

    def handle(self, key):
        action = self.vk_key_map.get(key.vk)

        if not action:
            action = self.chr_key_map.get(chr(key.c))

        return action if action else {}


class InputScheme:
    def __init__(self, keymaps):
        self.keymaps = keymaps

    def handle_key(self, key, game_state):
        action = {}

        # Keys defined for this game state will take priority over the defaults
        if self.keymaps.get(game_state):
            action = self.keymaps[game_state].handle(key)

        # Fall back to this input scheme's default mappings
        if not action and self.keymaps.get(None):
            action = self.keymaps[None].handle(key)

        # Fall back to the global default mappings
        if not action and self is not GLOBAL:
            action = GLOBAL.handle_key(key, game_state)

        return apply_modifiers(key, action)


NORTH = {'direction': (0, -1)}
SOUTH = {'direction': (0, 1)}
WEST = {'direction': (-1, 0)}
EAST = {'direction': (1, 0)}
NORTHWEST = {'direction': (-1, -1)}
NORTHEAST = {'direction': (1, -1)}
SOUTHWEST = {'direction': (-1, 1)}
SOUTHEAST = {'direction': (1, 1)}

GLOBAL = InputScheme(
    {
        None: KeyMap(
            {
                libtcod.KEY_UP: NORTH,
                libtcod.KEY_DOWN: SOUTH,
                libtcod.KEY_LEFT: WEST,
                libtcod.KEY_RIGHT: EAST,
                libtcod.KEY_F11: {'fullscreen': True},
                libtcod.KEY_ESCAPE: {'exit': True}
            },
            {
                'i': {'inventory': True},
            }),
        GameStates.PLAYER_TURN: KeyMap({},
            {
                'g': {'pickup': True},
                ',': {'pickup': True},
                ' ': {'wait': True},
                '.': {'wait': True},
            }),
        GameStates.PLAYER_DEAD: KeyMap({},
            {
                'r': {'restart': True}
            })
    })


class InputSchemes(Enum):
    LEFT_HAND = InputScheme(
    {
        None: KeyMap(
            {
                libtcod.KEY_TAB: {'inventory': True}
            },
            {
                'q': NORTHWEST,
                'w': NORTH,
                'e': NORTHEAST,
                'a': WEST,
                'd': EAST,
                'z': SOUTHWEST,
                'x': SOUTH,
                'c': SOUTHEAST
            }),
        GameStates.PLAYER_TURN: KeyMap({},
            {
                's': {'wait': True},
                'f': {'pickup': True}
            })
    })

    VI = InputScheme({
        None: KeyMap({},
            {
                'h': WEST,
                'j': SOUTH,
                'k': NORTH,
                'l': EAST,
                'y': NORTHWEST,
                'u': NORTHEAST,
                'b': SOUTHWEST,
                'n': SOUTHEAST
            })
    })

    NUMPAD = InputScheme({
        None: KeyMap(
            {
                libtcod.KEY_KP1: SOUTHWEST,
                libtcod.KEY_KP2: SOUTH,
                libtcod.KEY_KP3: SOUTHEAST,
                libtcod.KEY_KP4: WEST,
                libtcod.KEY_KP6: EAST,
                libtcod.KEY_KP7: NORTHWEST,
                libtcod.KEY_KP8: NORTH,
                libtcod.KEY_KP9: NORTHEAST
            },
            {}),
        GameStates.PLAYER_TURN: KeyMap(
            {
                libtcod.KEY_KP5: {'wait': True}
            },
            {})
    })
