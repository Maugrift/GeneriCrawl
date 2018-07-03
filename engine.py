from math import radians
from src.entity import Entity
from src.fov import *
from src.input import handle_keys
from src.map.game_map import GameMap
from src.render import render_all, clear_all


def main():
    # Size of the screen, in tiles
    screen_width = 80
    screen_height = 50

    # Size of the map, in tiles
    map_width = 100
    map_height = 100

    # The maximum number of tiles that can be seen in any direction, in tiles
    fov_radius = 10

    # The total span of the cone of vision, in radians
    fov_span = radians(140)

    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'GeneriCrawl', False)
    console = libtcod.console_new(screen_width, screen_height)
    game_map = GameMap(map_width, map_height)

    # Place the player and NPC in different locations
    player_tile = game_map.find_random_open_tile()
    npc_tile = game_map.find_random_open_tile()
    while npc_tile == player_tile:
        npc_tile = game_map.find_random_open_tile()

    player = Entity(player_tile[0], player_tile[1], 0.0, '@', libtcod.white)
    npc = Entity(npc_tile[0], npc_tile[1], 0.0, '@', libtcod.yellow)
    entities = [npc, player]

    recompute_fov = True
    fov_map = initialize_fov(game_map)
    memory = []

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    clear_all(console, entities, player.x, player.y, screen_width, screen_height)

    while not libtcod.console_is_window_closed():
        if recompute_fov:
            fov = compute_fov_angled(fov_map, player.x, player.y, fov_radius, player.facing, fov_span)
            update_memory(memory, fov)

        render_all(console, entities, game_map, fov, memory, player.x, player.y, screen_width, screen_height)
        libtcod.console_flush()
        libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, mouse, True)
        clear_all(console, entities, player.x, player.y, screen_width, screen_height)

        recompute_fov = False

        action = handle_keys(key)

        direction = action.get('direction')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if direction:
            move = action.get('move')
            face = action.get('face')

            dx, dy = direction
            if move and player.move(dx, dy, game_map):
                recompute_fov = True

            if face and player.face(atan2(dy, dx)):
                recompute_fov = True

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
    main()
